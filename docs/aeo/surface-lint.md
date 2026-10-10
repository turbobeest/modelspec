# Surface-consistency lint

**Status:** implemented by MODEL-255 in `pipeline/surface_lint.py`. Copy comes from the entity registry (MODEL-252) and `pipeline/agent_copy.py` (MODEL-257).

If the landing page, the docs, the MCP card and the JSON-LD describe ModelSpec in different words, an answer engine sees several entities and picks one at random. On 2026-10-01, five different one-liners were live. The lint makes drift fail CI instead of accumulating.

## Where it runs

| Mode | Input | On failure |
|---|---|---|
| CI | `dist/modelspec`, after the full build and after live assembly | The build fails |
| Weekly | Live `https://modelspec.dev`, unauthenticated MCP `tools/list` | Opens or updates **one** issue titled `AEO surface drift`; closes it when clean |

The weekly workflow also has `workflow_dispatch`. Runs serialize. A closed issue is reopened on new drift; duplicate open issues with that exact title are closed. `scripts/aeo/surface_drift.py` uses `gh` and accepts saved issue JSON with `--dry-run`, so its decisions can be checked offline.

## Checks

### 1. Presence

| Surface | Registry value |
|---|---|
| Landing title | `TITLE`, exact equality |
| Landing first paragraph, meta description, `og:description` | `ONE_SENTENCE` |
| `/method/` first paragraph; `llms.txt`, `index.md`, agent skill, brand page | `ONE_SENTENCE` |
| `/method/`, `llms.txt` | `DISAMBIGUATION` |
| MCP card description | `SHORT`, the registry's length-limited form |
| Landing `Organization.description` | `ONE_SENTENCE`, exact equality |

HTML comparison decodes entities, removes tags and normalizes whitespace. Superseded one-liners fail anywhere in owned copy. The README remains covered by `tests/test_entity.py`.

### 2. Banned lexicon

Owned copy includes HTML, `llms.txt`, Markdown twins, `.well-known/*.json`, `openapi.yaml` and `auth.md`. Scripts and styles are not prose; metadata and JSON-LD are checked. Each rule has a failing and passing fixture.

| Pattern (case-insensitive) | Why | Lifted when |
|---|---|---|
| "knowledge graph" as a self-description | Positioning: an analysis of alternatives | A positioning change |
| "router" as a self-description ("ModelSpec routes", "a model router that") | ModelSpec does not route requests | Never |
| `x402`, "pay per call without a key", "Bazaar" | `X402_ENABLED` is false | The PR that turns x402 on (MODEL-261) |
| `pip install modelspec`, an offline decision CLI, or a CLI data download | MODEL-307 ships the thin keyed `modelspec-dev` client; the `modelspec` package is unrelated | Never |
| Affirmative "sponsored", "featured partner", "promoted", "affiliate" claims | The matching paid-placement, provider-paid-visibility or referral-fee assertion in `neutrality_commitment()` is false | That assertion changes |
| A removed source, matched by `REMOVED_TEXT` in `decision/excluded.py` (reuse it; never restate the names) | MODEL-117 excluded sources | Never |
| A named competitor product in a comparison | Comparisons are by category | A decision by Jamie |

| Allowed wording | Why |
|---|---|
| "A router chooses per request"; the registry's no-routing claim | Describes another tool, or denies routing |
| The unrelated-package warning; `pip install modelspec-dev`; "no data download" | Does not offer the retired CLI |
| "No sponsored slots", "never earn affiliate fees" | Denies paid ranking; a negation does not exempt the next sentence |
| Benchmark authors "sponsored by" an institution, on `/b/` pages and their twins | Funding provenance, not ModelSpec placement |
| Conditional payment-rail references in adopted legal pages | Published disclosures must remain intact; affirmative "we accept/use/offer x402" promises still fail |

No legal page is excluded from the other rules. Product and agent copy must omit even negative references to the disabled rail. Wrangler's production vars decide whether that rule runs. Competitor matching uses a small list of router/gateway products and comparison phrases; model/provider comparisons and neutral product mentions are allowed.

### 3. JSON-LD

* It parses.
* It uses only the reviewed schema.org types in the lint's allowlist. The list covers the current generators and `Thing`; new types need review. External contexts and foreign type URLs fail.
* Every nested `name` and `description` also appears in the same page's body, after entity and whitespace normalization. Head metadata, scripts, styles, templates, SVG and hidden elements cannot satisfy it.

The landing's catalogue and machine-access disclosure uses the same nodes as JSON-LD. Breadcrumb labels use existing page headings. The full build's decide placeholder uses the live crawler capsule.

### 4. Agent surfaces

| Artifact | Check |
|---|---|
| Built MCP card | `SHORT`; exact generated card tool descriptions and complete tool names |
| `mcp/src/agent-copy.json` in tree mode | Exact generated tool descriptions and instructions |
| OpenAPI agent operations | Exact generated summary and lead; technical paragraphs may follow |
| Live MCP `tools/list` | Exact generated descriptions, including prices; missing, duplicate and unknown tools fail |

Expected short and long tool copy is regenerated in memory from `tiers.json`, so price drift fails too. Auth refusal or an unreachable MCP endpoint is reported as **not checked**, not drift; the static card is still checked when published. `--get-only` skips the MCP metadata POST. The weekly job permits that POST and calls no paid tools.

Holding mode is detected from the holding builder's sitemap-free robots file. Its file allowlist decides which missing pages and discovery files are not applicable. Existing landing, legal, brand and OpenAPI files still get checked. Holding intentionally does not inject landing JSON-LD.

### 5. Freshness

| Tree | Date check |
|---|---|
| Every sitemap | Valid dates, no later than `api/build.json`'s `built_at` |
| Full build | Every page carries the build date, as `pipeline.render.sitemap()` writes it |
| Assembled live tree | Each known page matches `pipeline.live.lastmod()` and `PAGE_SOURCES` |
| Deployed tree | Source-date equality only when its build commit matches the checkout; otherwise reported as not checked |

Gap: the live builder uses the last source commit, not dirty working-tree changes. The check trusts the declared source list and does not discover transitive dependencies. The live probe cannot establish source-change dates for a different deployed commit. It still checks the build-date upper bound.

## Output

One line per `Finding(surface, check, excerpt, expected)`, followed by notices and a count. Exit 1 on findings, 0 when clean. `--report` writes JSON for the weekly issue updater. Issue bodies are limited to 60,000 characters, with a truncation notice pointing to the complete workflow log.

```sh
python -m pipeline.surface_lint --tree dist/modelspec
python -m pipeline.surface_lint --live https://modelspec.dev --get-only
```

`tests/test_surface_lint.py` proves rejection of the old title, a self-described knowledge graph, the disabled payment rail and invisible JSON-LD claims. `tests/test_agent_ready.py` runs the lint on its existing real-build fixture.
