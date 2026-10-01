# JSON-LD generation

**Status:** the current generator is `pipeline/structured_data.py` (MODEL-218). The changes below are designed and implemented by MODEL-252.

## What ships today

`structured_data.inject(tree)` writes one `<script type="application/ld+json">` per page, holding a `@graph`:

| Page | Nodes |
|---|---|
| `/` | `Organization`, `WebSite`, `Dataset`, `WebAPI` + `SoftwareApplication` (the API), `SoftwareApplication` (the MCP server) |
| `/decide/` | `BreadcrumbList`, `WebApplication` (free offer) |
| Every other page in `CRUMBS` | `BreadcrumbList` |

`Organization.sameAs` comes from `brand/social/profiles.json`. Every handle there is empty, so no `sameAs` ships.

## Changes (MODEL-252)

1. **One source.** `Organization.description`, `og:description`, the landing meta description and the opening of `llms.txt` all read `one_sentence` from the entity registry. A test fails if any of them carries its own string.
2. **`sameAs` always present.** The site URL, the GitHub repository and the MCP endpoint come from the registry. Social profiles are added when `profiles.json` has a handle.
3. **`Dataset` survives MODEL-247.** `dataset()` reads its model count from `api/index.json`, which MODEL-247 removes. It already falls back to a count-free description. A test should pin the fallback so the node never claims a count it can't read.
4. **Explainer pages (MODEL-258)** get `Article` and, on the definition page only, `DefinedTerm`. `FAQPage` is used only where the questions and answers are visible on the page.
5. **`/graph/` leaves `CRUMBS`** when MODEL-251 removes the page.

## Rules

* **Markup matches visible text.** Every `name` or `description` in the JSON-LD also appears in the rendered page (Google's structured-data policy). The surface lint checks this.
* **Only schema.org types**, with stable `@id`s under `https://modelspec.dev/#…`.
* **No invented ratings or reviews.** That is why no `SoftwareApplication` gets a rich-result card, and that is correct.
* **No claims behind flags.** No `offers` that describe paid machine access while billing is off, and no payment-protocol properties while x402 is off.
* **Structured data is for disambiguation, not citations.** Google says generative search needs no special schema. JSON-LD is there to name the entity correctly and to qualify for ordinary rich results.
