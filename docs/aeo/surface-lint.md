# Surface-consistency lint

**Status:** design, implemented by MODEL-255. It depends on the entity registry (MODEL-252).

If the landing page, the docs, the MCP card and the JSON-LD describe ModelSpec in different words, an answer engine sees several entities and picks one at random. On 2026-10-01, five different one-liners were live. The lint makes drift fail CI instead of accumulating.

## Where it runs

| Mode | Input | On failure |
|---|---|---|
| CI | The built `modelspec.dev` tree | The build fails |
| Weekly | Live `https://modelspec.dev`, `api.modelspec.dev/mcp` `tools/list` | Opens or updates **one** GitHub issue, and closes it when clean |

## Checks

### 1. Presence

* `one_sentence` from the registry appears verbatim on each surface the registry lists:
  * the landing `<title>` area and meta description;
  * `og:description`;
  * the first paragraph of `/method/`;
  * the opening of `llms.txt`;
  * the `.well-known/mcp.json` description;
  * the `Organization` JSON-LD `description`.
* The README's first sentence matches too (repository test).
* The disambiguation line is on `/method/` and in `llms.txt`.

### 2. Banned lexicon

Owned surfaces must not contain these. Each rule names the decision behind it so it can be retired deliberately.

| Pattern (case-insensitive) | Why | Lifted when |
|---|---|---|
| "knowledge graph" as a self-description | Positioning: an analysis of alternatives | A positioning change |
| "router" as a self-description ("ModelSpec routes", "a model router that") | ModelSpec does not route requests | Never |
| `x402`, "pay per call without a key", "Bazaar" | `X402_ENABLED` is false | The PR that turns x402 on (MODEL-261) |
| The CLI described as current ("pip install modelspec", "the CLI lets you") | The CLI was retired on 2026-09-30 | Never |
| "sponsored", "featured partner", "promoted", "affiliate" | Neutrality commitment | Never |
| "Artificial Analysis", "Zapier" as a source | Excluded sources | Never |
| A named competitor product in a comparison | Comparisons are by category | A decision by Jamie |

Words such as "router" are allowed when they describe *other* tools, for example "a router chooses per request". The rule matches self-description patterns, not the bare word. Every pattern has a fixture that must fail and a fixture that must pass.

### 3. JSON-LD

* It parses.
* It uses only schema.org types.
* Every `name` and `description` value also appears in the page's visible text.

### 4. Agent surfaces

* The MCP card description and every MCP tool description come from the registry (MODEL-257).
* Prices in tool descriptions equal `api/worker/tiers.json`.

### 5. Freshness

* No sitemap `<lastmod>` is later than the build.
* A page whose source changed in this build carries the new date.

## Output

One line per finding: `surface`, `check`, the offending excerpt, and the registry value it should match. Exit code 1 in CI. The weekly job writes the same lines into the issue body.
