# Holding mode

`SITE_MODE` has been `live` since 2026-09-25. Checkout remains closed. This
document records the fail-closed holding tree and how the workflow derives it.

## The switch

One GitHub Actions repository variable, `SITE_MODE`, read by
`.github/workflows/deploy-sites.yml` ("Build and deploy the sites").

| `SITE_MODE` | Production (`--branch=main`) | Preview (`--branch=internal`) |
| --- | --- | --- |
| exactly `live` | real modelspec site, benchgraph redirect | real modelspec site, benchgraph redirect |
| unset, empty, or anything else | modelspec holding tree, benchgraph redirect | real modelspec site, benchgraph redirect |

A missing variable is holding. No merge can bring the old site back by accident.

Every run builds the real site with `pipeline.build`, as before, and then
`python -m pipeline.holding build` writes `dist-holding`. The build job's
summary names the mode and which tree production got.

The real tree serves the MODEL-186 landing at `/` and the decision board at
`/decide/`. The `internal` preview is a byte-identical copy. `/landing/`
permanently redirects to `/`.

`pipeline/live.py` composes that tree from the full build. It is an allowlist,
and it fails the build when llms.txt, the Markdown twin, a `.well-known` file,
the `Link` header or a published page names a path the tree lacks. After every
deploy, `python -m pipeline.live smoke` fetches each discovery file and page
from the preview, and from modelspec.dev when live (MODEL-214).

## benchgraph.dev

benchgraph.dev is redirect-only in both modes (MODEL-126). During holding its
pages land on modelspec.dev's dark 404, and its `/api/*` URLs redirect to
modelspec.dev's live `/api/*`. The benchmark pages now preview on the modelspec
internal preview (`/b/<id>/`), not the benchgraph one.

## What production serves while dark

modelspec.dev:

- `/`: the MODEL-186 landing page. It uses the decision snapshot's capability
  estimates and published offering prices. The board controls say "Board
  opening soon" while the board stays dark. The page has a canonical URL and is
  indexable.
- Every other HTML path: the existing dark holding message. Paths that no
  longer exist, such as model pages, benchmark pages, the wizard, the explorer,
  and `/pricing`, receive that message with a 404 status.
- `/api/**` on modelspec.dev, byte for byte what the real build publishes. The
  CLI (`modelspec snapshot fetch`), DPF, the rank Worker and the MCP server
  read only these paths. `benchgraph.dev/api/*` redirects to the same files.
  Tests: `tests/test_holding.py`.
- `/legal/**` and `/openapi.yaml` on modelspec.dev, byte for byte. Stripe's
  account review and past purchasers rely on the legal pages.
- `X-Robots-Tag: noindex` on every response except `/` and `/index.html`, and no
  `Link` header. Cloudflare Pages' more-specific header rules detach that header
  from the two landing paths using [the documented `! Header-Name`
  syntax](https://developers.cloudflare.com/pages/configuration/headers/#detach-a-header).
  robots.txt allows crawling and names no sitemap.
  The 404 page has a matching robots meta tag and no canonical. There is no
  sitemap, llms.txt, Markdown twin, `.well-known` file, or Pages Function.

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

The real modelspec site from `main` is always on the preview branch:

- https://internal.modelspec-7np.pages.dev

It is byte-identical to the live production tree. `/` is the landing and
`/decide/` is the board. Their canonical URLs name `modelspec.dev`.

https://internal.benchgraph.pages.dev serves the same redirect file as
production. It does not host the benchmark pages.

To check production is dark:

```bash
curl -sI https://modelspec.dev/ | grep -i x-robots-tag     # no output
curl -s  https://modelspec.dev/robots.txt                  # Allow: /, no Sitemap
curl -so /dev/null -w '%{http_code}\n' https://modelspec.dev/models/   # 404
curl -s  https://modelspec.dev/api/build.json              # the export, as ever
```

## Switch to live

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
