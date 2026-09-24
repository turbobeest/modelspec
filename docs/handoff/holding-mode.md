# Holding mode

Since 2026-09-24 modelspec.dev and benchgraph.dev show a holding page, and
Checkout is closed. Jamie's decision: the rankings are stale while the redesign
is under way, and the product is not to be seen until he says go. The data
stays up.

## The switch

One GitHub Actions repository variable, `SITE_MODE`, read by
`.github/workflows/deploy-sites.yml` ("Build and deploy the sites").

| `SITE_MODE` | Production (`--branch=main`: the two domains) | Preview (`--branch=internal`) |
| --- | --- | --- |
| exactly `live` | the real site | the real site |
| unset, empty, or anything else | the holding trees | the real site |

A missing variable is holding. No merge can bring the old site back by accident.

Every run builds the real site with `pipeline.build`, as before, and then the
holding trees from it with `python -m pipeline.holding build`. The build job's
summary names the mode and which tree production got.

## What production serves while dark

- `/` and every other HTML path: the holding page (the name, "… is in
  preparation. Check back soon.", Terms and Privacy on modelspec.dev, and
  © Sparks and Sawdust LLC). Paths that no longer exist, such as model pages,
  benchmark pages, the wizard, the explorer and `/pricing`, get the same page as
  a 404.
- `/api/**` on both domains, byte for byte what the real build publishes. The
  CLI (`modelspec snapshot fetch`), DPF, the rank Worker and the MCP server
  read only these paths. Tests: `tests/test_holding.py`.
- `/legal/**` and `/openapi.yaml` on modelspec.dev, byte for byte. Stripe's
  account review and past purchasers rely on the legal pages.
- `X-Robots-Tag: noindex` on every response, and no `Link` header. robots.txt
  allows crawling (a crawler must fetch a page to see its noindex) and names
  no sitemap. There is no sitemap, llms.txt, Markdown twin, `.well-known`
  file or Pages Function.

`api.modelspec.dev` (rank, policy-check, credits, MCP) is unchanged. Nothing on
the holding page links to it.

## Billing while dark

`BILLING_ENABLED` is `"false"` in `api/worker/wrangler.jsonc`. It gates
Checkout alone. `POST /v1/billing/checkout` and the `/pricing` form post
answer `503 billing_not_enabled` before any call to Stripe. The Stripe
webhook, claim and rotation keep working, so a refund or chargeback of a past
purchase still acts on its credits, and a renewal is still credited. Existing
keys keep their credits on `/v1/rank` and `/v1/policy-check`. Details:
[`../billing.md`](../billing.md).

## Test the real site

The real site from `main` is always on the preview branch:

- https://internal.modelspec-7np.pages.dev
- https://internal.benchgraph.pages.dev

It is the full site, links included. Its canonical URLs still name the
production domains.

To check production is dark:

```bash
curl -sI https://modelspec.dev/ | grep -i x-robots-tag     # noindex
curl -s  https://modelspec.dev/robots.txt                  # Allow: /, no Sitemap
curl -so /dev/null -w '%{http_code}\n' https://modelspec.dev/models/   # 404
curl -s  https://modelspec.dev/api/build.json              # the export, as ever
```

## Relaunch

Only when Jamie says go.

```bash
gh variable set SITE_MODE --body live
gh workflow run "Build and deploy the sites" --ref main
```

Start a new run as shown. Do not re-run an old one: a re-run repeats that run's
commit. The build summary must say `Site mode: live`.

To reopen Checkout as well, set `"BILLING_ENABLED": "true"` in
`api/worker/wrangler.jsonc`, run `python api/worker/openapi.py`, and merge; the
rank Worker deploys on push to `main`. Do both together: the buy buttons are on
`/pricing`, which only the live site publishes.

## Go dark again

```bash
gh variable set SITE_MODE --body holding   # or: gh variable delete SITE_MODE
gh workflow run "Build and deploy the sites" --ref main
```

Close Checkout with a PR that sets `"BILLING_ENABLED": "false"` and regenerates
`openapi.yaml`.
