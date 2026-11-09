# Moving ModelSpec to its own Cloudflare account (MODEL-441)

This runbook moves every ModelSpec resource out of the shared Cloudflare
account `43840d11…`, which dev-mux and personal sites also use, into a new
ModelSpec-only account. The sites and the free decide page keep answering
throughout. The API, keyless calls included, does not: on 2026-11-08
`api.modelspec.dev` was down for 36 minutes around activation (see "What the
2026-11-08 move found"); with the phase 8 `A` record, expect up to 15
minutes. Credit operations, which every keyed and paid call needs, freeze for
the minutes between exporting the ledger and the zone turning active, and
answer 503 meanwhile. No credit balance is lost or
counted twice.
Jamie's plan doc covers the account-level reasoning: "Cloudflare Account
Separation: dev-mux & modelspec", <https://claude.ai/artifact/CmPqJyGpcDMY3T3iw2DQrC>.

## The point of no return

All three ModelSpec-related domains are registered with **Cloudflare
Registrar** (RDAP and whois, read 2026-10-22). There is no nameserver change at
an outside registrar. A domain moves by an inter-account registration move:
the zone is first added to the new account (Pending), the old account
requests the move, and the new account approves it. Cloudflare's page says
the source account loses all of the domain's configuration, and the
registration is transfer-locked for 30 days afterwards
(<https://developers.cloudflare.com/registrar/account-options/inter-account-transfer/>).

So **approving the modelspec.dev move is the point of no return**. Everything
before it can be undone, and everything after it is fixed forward in the new
account. Every check in phases 1 to 7 exists to make that approval safe.
benchgraph.dev moves first as a rehearsal.

Workers routes need an active zone
(<https://developers.cloudflare.com/workers/configuration/routing/routes/#set-up-a-route>),
and the moved zone stays Pending in the new account until the move. So the new
account's Workers deploy without routes (`CF_ROUTES=off`), and
`scripts/cf_move.py attach-routes --wait-active` adds them about a second after
the zone turns Active. Phase 4 checks whether a Pending zone accepts routes
after all; on 2026-11-08 it did, so no route gap occurred. The API gap that
remains is the Pending window: Cloudflare's nameservers can answer from the
new zone before it is Active, and a Pending zone serves records unproxied, so
no Worker runs. Expect up to 15 minutes without the API.

## Inventory

Sources: the repository at `origin/main` 7e3d8ba6; the live account through
the Cloudflare connector (Workers, KV, R2 and D1 lists, read 2026-10-22);
public DNS and RDAP. Rows marked *read token* need Jamie's account-scoped read
token. The connector cannot see them.

| Resource | Where it is defined | State, 2026-10-22 | How it moves |
| -- | -- | -- | -- |
| Worker `modelspec-rank` | `api/worker/wrangler.jsonc` | live. Route `api.modelspec.dev/*` on zone modelspec.dev. Proxied `AAAA api → 100::` | redeploy by `rank-api.yml` into the new account |
| Worker `modelspec-mcp` | `mcp/wrangler.jsonc` | live. Routes `api.modelspec.dev/mcp*` and `/.well-known/mcp/server-card.json`. Service binding `RANK → modelspec-rank` (same account only) | redeploy by `mcp.yml` after rank |
| Worker `modelspec-rank-staging` | `env.staging` | live on workers.dev. Its own KV namespaces `modelspec-rank-staging-access` and `-determinations`. Its own DO namespaces | redeploy. Wrangler provisions its id-less KV. Staging data is disposable |
| KV `DETERMINATIONS` `a73f33d3…` | wrangler.jsonc | live. Written only by `api/worker/load_determinations.py` | `scripts/cf_move.py kv-merge` copy |
| KV `ACCESS` `ef86b7ce…` | wrangler.jsonc | live. Holds `key:` records, billing `session:` `sub:` `keyref:` `event:`, and rate counters `count:` (TTL ≤ 1 day) | copy, then a three-way merge after the move |
| DO `CreditsObject` (`CREDITS`, one instance `ledger`) | `credits_do.py` | one JSON document in SQLite | **export and import** across a short write freeze (below) |
| DO `HumanGateObject` (`HUMAN_GATE`) | `human_gate_do.py` | per-visitor daily admission state, used by the live visit gate | not moved. It starts empty in the new account (decision below) |
| Pages project `modelspec` | `deploy-sites.yml` | `modelspec.dev`, `www`, branches `internal` (`internal.modelspec-7np.pages.dev`) and `coverage` | new project, same name. **The `*.pages.dev` subdomain changes**: `modelspec-ax6` since 2026-11-08 |
| Pages project `benchgraph` | `deploy-sites.yml` | `benchgraph.dev`, `www.benchgraph.dev`, branch `internal` | new project, same name. Subdomain `benchgraph-et2` since 2026-11-08. Add `www.benchgraph.dev` as a custom domain too |
| Zone `modelspec.dev` | Cloudflare Registrar since 2026-09-07 | NS `alex`/`laylah.ns.cloudflare.com`. No DS at the registry (`delegationSigned: false`). Email Routing MX. SPF (Google and Cloudflare). DMARC `p=none`. Google site verification | registrar inter-account move |
| Zone `benchgraph.dev` | Cloudflare Registrar since 2026-09-07 | same nameservers, no DS, no MX | registrar move, **first, as the rehearsal** |
| Zone `sparksandsawdust.com` | Cloudflare Registrar since 2026-03-13 | Worker `sparksandsawdust-com` (modified 2026-10-03). Email Routing MX. `hello@sparksandsawdust.com` is the DMCA contact in `docs/legal/dmca.md` | **Jamie decides the owner** (HEY JAMIE list) |
| Email Routing | per zone, with destinations per account | `sales@modelspec.dev` is published in 17 places. `hello@sparksandsawdust.com` is legal | recreate rules. Jamie re-verifies each destination address by email |
| Turnstile widget | account | site key in repo variable `TURNSTILE_SITE_KEY`, secret in Worker secret `TURNSTILE_SECRET` | new widget after the move. Hostname-allowlisted widgets keep working across accounts until then |
| Worker secrets | Worker settings | names from the code: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `TURNSTILE_SECRET`, `VISIT_TOKEN_HMAC_KEY`, `VISITOR_HMAC_KEY`, `CDP_API_KEY_ID`, `CDP_API_KEY_SECRET`, `PUSHOVER_APP_TOKEN`, `PUSHOVER_USER_KEY`, `MODELSPEC_SNAPSHOT_KEY` (synced by CI), and when their features are on `SIGNALS_HMAC_SECRET`, `SIGNALS_READ_KEY`, `DECISION_LINK_HMAC_KEY`, `FEEDBACK_LIMIT_PEPPER`. New: `LEDGER_ADMIN_SECRET` | *read token*: `wrangler secret list` on each Worker is the authoritative list. Jamie sets them |
| Worker vars | wrangler.jsonc | production switches and x402 settings | travel with the config |
| GitHub secrets | repo-level | `CLOUDFLARE_ACCOUNT_ID` (deploy-sites, coverage-slo, rank-api, mcp), `CLOUDFLARE_API_MODELSPEC_TOKEN` (rank-api, mcp), `CLOUDFLARE_API_TOKEN` (deploy-sites, coverage-slo). `modelspec-data` holds no Cloudflare secret | new values (Jamie) |
| Account plan and add-ons | account | Python Workers and Durable Objects run on the old account's Workers plan | *read token*. The new account needs the same Workers plan before the first deploy |
| Zone settings, rules, certificates | zone | not carried by a DNS export | `cf_move.py zone-dump` on both sides, then `zone-diff` until nothing is left but what is expected |

Not ModelSpec, so it stays: R2 `devmux-backups`; D1 `dev_mux_cp`, `dev_mux_cp_test`
and `dsf-landing-db`; Workers `dev-mux-*`, `status-proxy`, `terbeest-*` and the
parked-domain Workers; KV `WAITLIST`, `CANARY_MAIL` and the dev-mux namespaces.
`WAITLIST` and `status-proxy` have no owner in the repo. The read token shows
their bindings.

## Decisions

**KV.** Copy each namespace once with `scripts/cf_move.py kv-merge --base empty
--save-src <base>`. The saved source snapshot is the base for later merges.
After the move, the old Worker stops taking writes. One more `kv-merge --base
<base>` then applies only what the old side changed since the base, and only
where the new side has not changed the same key. Keys changed on both sides
are reported as conflicts and never overwritten. Rate counters (`count:`) are
skipped: they expire within a day and do not carry money. API keys keep
working because their `key:` records are copied byte for byte. A key bought
or rotated between the copy and the move is missing on the new side only
until the merge runs. Run the merge as soon as the old Worker goes quiet.

**Credit ledger.** A Durable Object cannot move between accounts, so the
ledger moves across a short write freeze (`api/worker/src/ledger_admin.py`,
`api/worker/src/credits_do.py`). We have no paying customers yet, so a few
minutes of 503 on credit operations is the right price for the simplest
procedure. An earlier version kept credits live by forwarding calls between
the two Workers. Six review rounds kept finding new interleavings in it, so it
was dropped.

Each ledger has a role: `live` serves calls, `standby` waits for its one
import, and `sealed` has been exported and serves nothing. The new account's
ledger starts in `standby` (`CF_LEDGER_STANDBY=true` adds the var
`LEDGER_STANDBY`), so nothing writes to it early. The move:

1. `POST /internal/ledger/export` on the old Worker seals its ledger in the
   same write that reads the copy, and returns the copy with its digest and
   holder count.
2. `POST /internal/ledger/import` on the new Worker loads the copy into the
   standby ledger, which turns live.
3. The digests and holder counts must match.

The final ACCESS merge runs between the two (phase 8). Neither ledger is live
then, so neither Worker writes key records, and the merge cannot overwrite a
revocation or rotation it did not see. Requests already running when the
freeze begins are covered by leases. Every billing mutation (webhook, claim,
rotation) takes a 120-second lease on the live ledger before it writes, and
each of its KV writes re-checks that lease. The first export call moves the
ledger to `draining`: no new lease is granted, so the open ones end within
120 seconds however much traffic arrives, and the seal follows once they
have. A request that outlives its lease has its writes refused. `kv-merge --final` reads the
source only after it has been sealed for 120 seconds, and `kv-merge --apply`
checks the destination's ledger is frozen before and after it writes. Only a standby
ledger that holds no balances accepts a copy, or a rolled-back one that took
no writes. Each export carries a generation number, so a rolled-back
destination takes a fresh export but never a replay of the copy it was rolled
back from.

At most one ledger is live at any moment, and none during the freeze, so no
balance is lost or counted twice. Export and import can be repeated safely:
export returns the same copy, and the copy lands once.

A ledger that is not live raises `LedgerUnavailable`, and the Worker answers
503 with `retry-after: 5`. Error text that merely looks like a freeze never
counts as one: the adapter reads the Durable Object's status first. The
endpoints exist only while `LEDGER_ADMIN_SECRET` is set. Without it they
answer the ordinary 404. Nothing calls another Worker: the copy travels
through the operator's machine.

**Stripe webhooks.** The endpoint URL, `https://api.modelspec.dev/v1/billing/stripe-webhook`,
does not change, so Stripe needs no change. Both Workers carry the same
`STRIPE_WEBHOOK_SECRET`, so whichever one Cloudflare routes an event to
verifies it. During the freeze, every webhook answers 503 before it writes
anything, unremembered, and Stripe retries it, for up to three days, until it
reaches the new Worker. Claims and key rotations are refused the same way. `LedgerUnavailable` is deliberately not a
`StoreNotConfigured`, because several billing paths treat an unbound ledger
as "carry on without credits". A key rotation moves the balance before it
revokes the old key, so a rotation refused by the freeze leaves the old key
working. x402 checks the ledger before it settles a payment, so a frozen
ledger refuses the payment instead of taking it, and a one-shot's credit and
spend are one ledger step. An event the old Worker was processing when the
freeze began may have written KV before its ledger call failed. The final
merge carries those writes, and Stripe's retry applies the event again on the
new Worker.

**Human gate.** Not migrated. Its state is one visitor-day of admissions.
Starting empty gives a visitor at most one extra day's allowance on the day
of the move. Visit tokens are HMACs under `VISIT_TOKEN_HMAC_KEY`. If Jamie
sets the same value in both accounts, tokens issued by one Worker verify on
the other. A new value only makes browsers verify once more.

**TLS.** A newly active zone gets its Universal certificate "within 15 minutes
to 24 hours". Cloudflare's way to avoid that gap is an Advanced certificate
ordered while the zone is Pending, which "deploys automatically once the
domain is active" (<https://developers.cloudflare.com/ssl/edge-certificates/universal-ssl/enable-universal-ssl/#minimize-downtime>).
That is Advanced Certificate Manager, a paid add-on, for modelspec.dev. Its
TXT validation records go into the old zone, which is still authoritative.
The benchgraph.dev rehearsal, run without one, measures the real gap for a
Pages-only zone.

**Pages.** Same project names in the new account. Custom domains are added
while the zone is Pending and validate on activation. The new projects get
new `*.pages.dev` subdomains, so PR-B (phase 9) replaces `modelspec-7np`
everywhere it appears.

**CI targeting.** Wrangler prefers the config's `account_id` over
`CLOUDFLARE_ACCOUNT_ID` (checked in Wrangler 4.134.0, `getActiveAccountId`).
Before this change the GitHub secret could not choose the account at all.
Deploy jobs now run `.github/scripts/cloudflare_target.py`, which rewrites
the CI checkout's `account_id`, KV ids and `workers_dev` from the job's GitHub
environment. The committed config keeps naming one account, so operators'
local wrangler commands still reach the right one. The Worker and Pages
deploy workflows take a `cloudflare_environment` input, defaulting to
`production`. A run with `cloudflare-modelspec` deploys the same commit into
the new account, and its smoke tests probe the workers.dev hosts named by
`CF_RANK_HOST` and `CF_MCP_URL`. `CF_ROUTES` and `CF_LEDGER_STANDBY` stop any
deploy to the `production` environment, so a variable set at the wrong scope
cannot strip the serving Worker's routes or freeze its ledger.

## Phases

Who does each step: **J** is Jamie (credentials, money, approvals), **A** is
an agent session with the tokens Jamie hands it, never printing them.

### Phase 0. Land the code (A, then J merges)

1. Review this PR cross-model and merge it. Production deploys still go to the
   old account, because the old secret equals the committed `account_id`.
   Nothing changes for callers.

### Phase 1. The new account (J)

1. Create the ModelSpec account, with its own admin login and 2FA.
2. Subscribe it to the same Workers plan the old account has. Pick its
   workers.dev subdomain, `<sub>` below.
3. Create four account-scoped API tokens:
   - **workers deploy** (new account): Workers Scripts Edit, Workers KV Storage
     Edit, Workers Routes Edit on modelspec.dev, Account Settings Read. This
     mirrors the current `CLOUDFLARE_API_MODELSPEC_TOKEN`.
   - **pages deploy** (new account): Cloudflare Pages Edit.
   - **migration** (new account, delete it after phase 10): Workers KV Storage
     Edit, Zone Edit, DNS Edit, Zone Settings Edit, SSL and Certificates Edit,
     Email Routing Rules Edit, Account Rulesets Edit, Single Redirect Edit,
     Turnstile Edit, Cloudflare Pages Edit, and Workers Routes Edit on modelspec.dev and benchgraph.dev
     (phases 7 and 8 attach the API routes with it).
   - **read** (old account, delete it after phase 10): Account Settings Read,
     Workers Scripts Read, Workers KV Storage Read, Pages Read, Zone Read, DNS
     Read, Zone Settings Read, SSL and Certificates Read, Email Routing Rules
     Read, Account Rulesets Read, Turnstile Read.
4. In GitHub, create environment `cloudflare-modelspec`. Add secrets
   `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_MODELSPEC_TOKEN` (workers deploy) and
   `CLOUDFLARE_API_TOKEN` (pages deploy). Phase 3 adds its variables.

### Phase 2. Full inventory (A, read token)

1. `python3 scripts/cf_move.py zone-dump --account <old> --zone modelspec.dev --out ~/cf-move/old-modelspec.json`.
   Do the same for benchgraph.dev and sparksandsawdust.com. Dumps go outside
   the repository, mode 0600.
2. List the Worker secrets of `modelspec-rank`, `modelspec-mcp` and
   `modelspec-rank-staging`, the Pages projects and their custom domains, the
   Turnstile widgets, the Email Routing destination addresses, the account's
   subscriptions, and the bindings of `WAITLIST` and `status-proxy`.
3. Fill in the *read token* rows above. Post the result on MODEL-441.

### Phase 3. Build the new account (A with the migration token, J where marked)

1. Create KV namespaces `ACCESS` and `DETERMINATIONS`. In GitHub environment
   `cloudflare-modelspec`, never at repository level, set variables
   `CF_TARGET_ACCOUNT_ID` to the new account's id, `CF_KV_ACCESS` and
   `CF_KV_DETERMINATIONS` to the namespace ids, and set
   `CF_WORKERS_DEV=true`, `CF_ROUTES=off`, `CF_LEDGER_STANDBY=true`,
   `CF_RANK_HOST=modelspec-rank.<sub>.workers.dev` and
   `CF_MCP_URL=https://modelspec-mcp.<sub>.workers.dev/mcp`.
2. Add zones modelspec.dev and benchgraph.dev to the new account, on the plan
   the old zones use. They stay Pending.
3. Import each zone's DNS from the old zone's BIND export, then review the
   proxied records. Run `zone-dump` on the new zone and `zone-diff` it against
   the old one. Recreate settings, rules, redirects and the AI-crawler
   settings until the diff shows only identities, nameservers and
   certificates.
4. Email Routing on the new modelspec.dev: add destination addresses (**J**
   clicks each verification email), then recreate the rules and the catch-all
   from the dump. Cloudflare refuses to enable Email Routing on a Pending zone
   (code 2009), so import the MX, SPF and DKIM records as plain DNS records now
   and enable routing once the zone is Active. Routing adopts the existing
   records without duplicating them.
5. **J** orders an Advanced certificate for `modelspec.dev, *.modelspec.dev`
   with TXT validation. A, or J, adds the `_acme-challenge` TXT records it
   shows to the **old** zone. Wait until it reads Holding Deployment or
   Pending Deployment.
6. Create Pages projects `modelspec` and `benchgraph` (production branch
   `main`). Dispatch `deploy-sites.yml` on main with
   `cloudflare_environment=cloudflare-modelspec`. Add the custom domains
   `modelspec.dev`, `www.modelspec.dev`, `benchgraph.dev` and
   `www.benchgraph.dev`. They stay pending
   until their zones activate. Note the new `*.pages.dev` subdomains.

### Phase 4. Deploy the Workers into the new account (A dispatches, J sets secrets)

Freeze merges to main from here to the end of phase 9, so both accounts run
the same commit.

1. Dispatch `rank-api.yml` on main with `cloudflare_environment=cloudflare-modelspec`.
   The deploy creates the Worker and both DO classes, without routes. Its
   ledger starts in standby and stays there until phase 8, so keyed calls on
   the workers.dev host answer 503 and the deploy drops the smoke key. Then
   try one dispatch with `CF_ROUTES` unset. If Wrangler attaches the routes to
   the Pending zone, keep it unset and skip `attach-routes` in phase 8. If it
   refuses, set `CF_ROUTES=off` again.
2. **J** sets every Worker secret from the phase 2 list on the new
   `modelspec-rank`. Use the same values for `STRIPE_WEBHOOK_SECRET` (shown in
   the Stripe dashboard), `TURNSTILE_SECRET` (the old widget's, for now) and,
   if he has them, `VISIT_TOKEN_HMAC_KEY` and `VISITOR_HMAC_KEY`. Prefer a new
   restricted Stripe key and new CDP keys over reusing old ones. Set a random
   `LEDGER_ADMIN_SECRET` on both the old and the new `modelspec-rank`.
3. Dispatch `rank-api.yml` again, so smoke tests run with the secrets in place.
   Then dispatch `mcp.yml` with the same input.
4. Check: `/v1/health`, decide, rank, policy-check and the MCP `tools/list` on
   the workers.dev hosts, and `GET /internal/ledger/status` on both Workers with
   the admin secret: old `live`, new `standby`. MCP refuses any `Host` but
   `api.modelspec.dev` and localhost (`mcp/src/server.ts`), so on workers.dev
   its smoke answers 403 "Invalid Host" until the allowlist names that host.
   Without that change, check MCP through `api.modelspec.dev` after phase 8.

### Phase 5. Copy KV (A, read token on the old side, migration token on the new)

```bash
export CF_SRC_API_TOKEN=… CF_DST_API_TOKEN=… LEDGER_ADMIN_SECRET=…   # never echoed
NEW=https://modelspec-rank.<sub>.workers.dev
python3 scripts/cf_move.py kv-merge --base empty --src-account <old> --src-namespace a73f33d391f74c3e88e45f47d8e50814 \
  --dst-account <new> --dst-namespace <new DETERMINATIONS> --dst-worker $NEW --apply
python3 scripts/cf_move.py kv-merge --base empty --src-account <old> --src-namespace ef86b7ce138d4891b3eb630cdd2ba4e5 \
  --dst-account <new> --dst-namespace <new ACCESS> --dst-worker $NEW --save-src ~/cf-move/access-base.json --apply
```

Both must report 0 conflicts. Keep `access-base.json` until phase 10.

`--apply` refuses unless the destination Worker's ledger is frozen (standby
or sealed) both before it reads and after it writes. A frozen ledger makes
the Worker refuse every write to key records, so nothing on the destination
can change a key between the merge's read and its write. The source may keep
changing: each run carries what changed there since the base.

Re-run the ACCESS merge with `--base ~/cf-move/access-base.json` (dry run,
then `--apply`) daily until phase 8. Each run carries the old side's new keys,
rotations and revocations across. Repeated runs are safe: a key already
carried matches on both sides and drops out of the plan.

### Phase 6. Rehearse on benchgraph.dev (J requests and approves, A watches)

1. A starts a probe that logs status code, TLS issuer and Pages deployment id
   for `https://benchgraph.dev/` every 2 seconds.
2. **J** requests the registrar move of benchgraph.dev from the old account
   and approves it in the new one.
3. Record how long the zone took to turn Active, and any window of TLS errors
   or 5xx. If there was a gap without an Advanced certificate, phase 3 step 5
   is required for modelspec.dev. Otherwise it is insurance.

### Phase 7. Prove the route token (A, migration token)

```bash
CF_API_TOKEN=… python3 scripts/cf_move.py attach-routes --account <new> --zone modelspec.dev --probe
```

It creates a throwaway route with no Worker on the Pending zone and deletes
it at once. Only `probe ok` lets phase 8 start. Without it, phase 8 would
leave `api.modelspec.dev` without its Workers after the irreversible move.

### Phase 8. Move the ledger, then modelspec.dev (J approves; the point of no return)

Pre-flight (A posts the evidence on MODEL-441 before step 2): every host
served only by a Worker has a proxied `A` record as well as its `AAAA`
(`api` → `192.0.2.1` and `100::`); the new rank Worker passes smoke on
workers.dev (MCP only if its allowlist names that host, phase 4 step 4); the new ledger is `standby`; `zone-diff` is clean;
the route probe passed; the Advanced certificate is waiting for deployment;
Email Routing destinations are verified; Pages custom domains are pending; the
rehearsal showed no unexplained gap. Run steps 2 to 5 in the quietest hour,
with Jamie ready to approve at once: credit operations answer 503 from step 2
until the zone is active.

1. A starts probes on `https://api.modelspec.dev/v1/health`, `https://modelspec.dev/`
   and `https://api.modelspec.dev/mcp`, and starts the route watcher with the
   migration token:

   ```bash
   python3 scripts/cf_move.py attach-routes --account <new> --zone modelspec.dev --wait-active \
     --route 'api.modelspec.dev/*=modelspec-rank' \
     --route 'api.modelspec.dev/mcp*=modelspec-mcp' \
     --route 'api.modelspec.dev/.well-known/mcp/server-card.json=modelspec-mcp'
   ```

2. Export the old ledger. That seals it, and releases any hold a request left
   in flight (those requests fail with 503 and are not charged). If it
   answers 409 with "draining", new billing requests are already refused and
   the ones in flight are finishing: run it again after the seconds it names,
   at most 120. `POST /internal/ledger/unseal` with `{}` cancels a drain. From here on
   the old Worker refuses billing writes before they touch KV, and Stripe
   retries its webhooks. Run no key script (`scripts/issue_api_key.py`,
   `scripts/revoke_api_key.py`) until step 7: they write KV directly.

   ```bash
   H='authorization: Bearer '"$LEDGER_ADMIN_SECRET"
   NEW=https://modelspec-rank.<sub>.workers.dev
   curl -sS -X POST https://api.modelspec.dev/internal/ledger/export -H "$H" > ~/cf-move/ledger.json
   ```

3. Run the final ACCESS merge. It refuses until the old ledger has been
   sealed for 120 seconds, so every write admitted before the freeze has
   landed. Both ledgers are frozen, so no Worker writes key records on either
   side:

   ```bash
   python3 scripts/cf_move.py kv-merge --final --base ~/cf-move/access-base.json --src-account <old> \
     --src-namespace ef86b7ce138d4891b3eb630cdd2ba4e5 --dst-account <new> --dst-namespace <new ACCESS> \
     --src-worker https://api.modelspec.dev --dst-worker $NEW --apply
   ```

   Re-run it until it reports `0 put, 0 delete`. Resolve each conflict key by
   hand, and read both sides first.
4. Import the ledger into the new Worker:

   ```bash
   jq '{state, digest, generation}' ~/cf-move/ledger.json | curl -sS -X POST "$NEW/internal/ledger/import" \
     -H "$H" -H 'content-type: application/json' --data-binary @-
   ```

   The export said `role: sealed` and the import says `role: live`, with the
   same `digest` and `holders`. Post the holder count on MODEL-441. That is
   the number of balances that moved. Call nothing else on `$NEW`.
5. **J** requests the move and approves it. On 2026-11-08, public DNS
   answered from the new zone about 5 minutes after the approval, while that
   zone was still Pending, and it turned Active about 19 minutes after the
   approval (benchgraph.dev took 12). A Pending zone serves its records
   unproxied, so Worker routes do not run until it is Active.
6. Unset `CF_ROUTES` in environment `cloudflare-modelspec` straight away.
   Wrangler replaces a Worker's whole route set on deploy, so a dispatch with
   `CF_ROUTES=off` would now remove the live routes. The 6-hourly scheduled
   `rank-api.yml` run still targets the old account until phase 9. It fails
   there, because the zone has left the old account, and that failure is
   expected.
7. When the zone is Active: `GET https://api.modelspec.dev/internal/ledger/status`
   with the admin secret must show `role: live`, which means the new Worker
   answered. Run decide, rank, policy-check, MCP and `/v1/credits` smoke
   against `api.modelspec.dev`, and load `/decide/` in a browser.
8. Send a test email to `sales@modelspec.dev`.

Rollback, before step 5 only. Always seal the new ledger before unsealing the
old one:

1. `GET $NEW/internal/ledger/status`.
   - `standby`: the import never landed. Go to step 3.
   - `live`: `POST $NEW/internal/ledger/export`, which seals it.
2. Compare that export's `digest` with the one in `~/cf-move/ledger.json`.
   - Equal: the new ledger took no writes. Go to step 3.
   - Different: the new ledger took writes, and it is now the real one.
     `POST $NEW/internal/ledger/unseal` with its new digest, stop the
     rollback, and fix forward. Never unseal the old one in this case.
3. `POST https://api.modelspec.dev/internal/ledger/unseal` with
   `{"digest": "<digest from ledger.json>"}`. The old ledger serves again.

The KV merge needs no undo: the old namespace was only read.

### Phase 9. Point main at the new account (J switches secrets, A writes PR-B)

PR-B, prepared before phase 8 and merged right after the secrets switch:

- `account_id` and both KV ids in `api/worker/wrangler.jsonc`; `account_id` in
  `mcp/wrangler.jsonc`.
- The new `*.pages.dev` subdomain in place of `modelspec-7np` in
  `api/worker/src/entry.py` (`CORS_ORIGINS`), `qa/tools.py`,
  `scripts/slo/targets.yaml`, `docs/method/coverage-slo.md` and
  `.github/workflows/deploy-sites.yml`.
- Inventory and comment dates updated in this runbook and the wrangler
  comments.

**J** replaces the repo-level `CLOUDFLARE_ACCOUNT_ID`,
`CLOUDFLARE_API_MODELSPEC_TOKEN` and `CLOUDFLARE_API_TOKEN` with the new
account's values, then deletes environment `cloudflare-modelspec`. Either
order of secret switch and merge fails safe: a deploy that mixes accounts
names a KV namespace the account does not have, and Wrangler refuses it. The
next staging deploy provisions staging's KV in the new account.

### Phase 10. Finish (A and J)

1. Turnstile: **J** creates a widget in the new account for `modelspec.dev`,
   `www.modelspec.dev` and the new internal preview host. He sets
   `TURNSTILE_SECRET` on the Worker and repo variable `TURNSTILE_SITE_KEY`
   together, then main redeploys the sites. Pages still cached with the old
   site key fail verification once and recover on reload.
2. Remove `LEDGER_ADMIN_SECRET` from both Workers. Open the follow-up PR that
   deletes `ledger_admin.py`, the export, import and unseal methods, and the
   `cloudflare_environment` input.
3. When the Universal certificate is Active, cancel the Advanced certificate.
4. sparksandsawdust.com, if Jamie assigns it here. Fetch the
   `sparksandsawdust-com` Worker's script with the read token, since its
   source is not in this repository. Recreate it and the hello@ routing, then
   move the domain as in phase 8.
5. After a 7-day hold, **J** deletes from the old account: Workers
   `modelspec-rank`, `modelspec-mcp` and `modelspec-rank-staging`, which also
   deletes their Durable Object data; KV `ACCESS`, `DETERMINATIONS` and both
   staging namespaces; Pages projects `modelspec` and `benchgraph`; the old
   Turnstile widget; the old `CLOUDFLARE_API_MODELSPEC_TOKEN` and Pages token;
   the read and migration tokens. Archive a final `kv-snapshot` of both old
   namespaces and the sealed ledger's status first.

## What the 2026-11-08 move found

The move ran on 2026-11-08 EST: benchgraph.dev from 17:29 (requested) to 17:42
(Active), modelspec.dev from 18:04 (requested) to 18:29 (Active). Every credit
balance moved (7 holders, digest unchanged). These gaps are folded into the
phases above; the list is the record.

- **API outage, 18:15 to 18:51 (36 minutes).** `api.modelspec.dev` was down,
  keyless calls included; the site and the decide page served throughout. Two
  causes, one after the other. From 18:15, about 5 minutes after the
  approval, Cloudflare's nameservers answered from the new zone while it was
  still Pending, which serves records unproxied, so clients reached `100::`
  and were refused. After activation at 18:29, the new zone gave the
  AAAA-only host no IPv4 address; the old zone had synthesized one. A proxied
  `A api → 192.0.2.1`, added at 18:36, resolved from 18:51. Phase 8 pre-flight
  now requires that record. The Pending window has no fix in this runbook:
  expect up to 15 minutes without the API, and pick the hour for it. The
  rehearsal missed both, because benchgraph.dev has no Worker-only host.
- **Error 1010.** Cloudflare refuses Python-urllib's default `User-Agent` on
  workers.dev, so `cf_move.py kv-merge` got 403 from the destination Worker.
  `cf_move.py` now sends its own agent.
- **Routes on a Pending zone.** Wrangler attached the Worker routes to the
  Pending zone, so `CF_ROUTES` stayed unset and `attach-routes` was not needed.
- **Tokens.** An account-owned token cannot read Page Rules (error 1011);
  check them in the dashboard. Writing Redirect Rules needs Single Redirect
  Edit, which the migration token lacked; Jamie created them in the dashboard.
- **Email Routing** cannot be enabled on a Pending zone (phase 3 step 4).
- **Advanced certificate.** The order needs a certificate authority chosen;
  Google Trust Services worked. It adds Advanced Certificate Manager, about
  $10 a month, until phase 10 cancels it.
- **MCP on workers.dev.** `mcp/src/server.ts` allows only `api.modelspec.dev`
  and localhost as `Host`, so MCP smoke on the workers.dev host answers 403
  "Invalid Host". MCP was checked through `api.modelspec.dev` after
  activation. A later move should add the transition host to the allowlist.
- **Stripe** had no webhook destination in live or sandbox mode, so there was
  no `STRIPE_WEBHOOK_SECRET` to carry. The new Worker has none. That gap
  predates the move and is tracked separately.

## Rollback

| After | Undo |
| -- | -- |
| Phases 0 to 5 | Nothing in production changed. Delete the new account's resources, or leave them. |
| Phase 6 | benchgraph.dev cannot move back for 30 days. Fix forward in the new account. Nothing else has moved. |
| Phase 7 | Nothing to undo: the probe route is deleted at once. |
| Phase 8, before step 5 | Seal the new ledger, check it took no writes, unseal the old one (phase 8 rollback). |
| Phase 8 approval | No move back for 30 days. Fix forward: `wrangler rollback` the new Workers, re-run the KV merge, redeploy Pages. The old account cannot serve the zone again. |
| Phase 9 | Revert PR-B and restore the old secrets only to recover CI. Production stays in the new account. |

## Residual risks

- Up to 15 minutes without `api.modelspec.dev` while Cloudflare answers from
  the Pending zone, which serves records unproxied. A few seconds of 522 at
  activation as well, if a Pending zone refuses routes (phase 4 step 1).
- The Pages sites get their certificates from Pages after activation. Advanced
  certificates do not apply to Pages custom domains
  (<https://developers.cloudflare.com/pages/platform/known-issues/>), so the
  site may show TLS errors for minutes. The benchgraph.dev rehearsal measures
  it. The API is not affected.

- Cloudflare does not document how traffic switches at a Registrar
  inter-account move. The benchgraph.dev rehearsal is the measurement.
- Credit operations answer 503 from the phase 8 export until the zone is
  active, which is minutes when the registrar move is approved straight
  away. Keyed and paid API calls fail during that time, Stripe retries its
  webhooks, and the free decide page is unaffected.
- A billing request that runs longer than its 120-second lease has its later
  KV writes refused and answers 503. For a key rotation caught this way, the
  balance has already moved to a new key that was never shown. Find that
  key's `key:` record (same owner, created at that minute) and move the
  balance back with `POST /internal/ledger/transfer` and
  `{"src": "key:<unseen fingerprint>", "dst": "key:<old fingerprint>"}`.
- A pack bought through x402 whose ledger freezes between settlement and the
  credit gets a 503 naming the settlement, and the credit is reconciled by
  hand from the Worker log's settlement record. A one-shot is credited and
  spent in one step, so it is either served normally or served unrecorded.
