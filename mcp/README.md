# ModelSpec remote MCP server

Read-only MCP tools over the ModelSpec catalogue. Data tools require an
API key. The site stays on Cloudflare Pages; this Worker only answers
`https://api.modelspec.dev/mcp` and its public server card at
`https://api.modelspec.dev/.well-known/mcp/server-card.json`.

## Official registry listing

The root `server.json` describes the keyed remote server using the official
registry's `2025-12-11` schema. Its checked-in version records the deployment
observed when the listing was added. The schema is vendored unchanged in
`tests/fixtures/mcp_registry/` so validation runs offline.

After review, merge, and a successful MCP deployment, an operator can dispatch
`Publish MCP registry listing` on `main`. It verifies that the live Worker's
`serverInfo.version` matches the selected commit and writes that version to a
temporary manifest. A deployment mismatch fails before authentication or
publication. The workflow uses checksum-pinned `mcp-publisher` v1.8.1 and GitHub
OIDC. It has no push trigger and needs no registry secret.

Registry metadata declares a required, secret `Authorization: Bearer` key.
Keys come from [pricing and keys](https://modelspec.dev/pricing/).

Sources: [registry schema](https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json),
[official publishing workflow](https://github.com/modelcontextprotocol/registry/blob/v1.8.1/docs/modelcontextprotocol-io/github-actions.mdx),
and [publisher v1.8.1](https://github.com/modelcontextprotocol/registry/releases/tag/v1.8.1).

## Smithery listing

After review, merge, and a successful MCP deployment, publish the remote URL
with the required API-key configuration below. Replace `YOUR_SMITHERY_NAMESPACE`
with the namespace owned by the publishing account:

```bash
smithery mcp publish "https://api.modelspec.dev/mcp" \
  -n @YOUR_SMITHERY_NAMESPACE/modelspec \
  --config-schema '{"type":"object","properties":{"apiKey":{"type":"string","title":"ModelSpec API key","description":"Create one at https://modelspec.dev/pricing/","x-from":{"header":"x-api-key"},"x-to":{"header":"x-api-key"}}},"required":["apiKey"]}'
```

Smithery collects each user's ModelSpec key and forwards it as the raw
`x-api-key` header value. The MCP Worker converts it to
`Authorization: Bearer <key>` for API calls. This alias applies only to MCP;
direct `/v1/*` API calls still accept only Bearer authentication.

The public server card requires no key. Its `serverInfo` matches `initialize`,
including the deployed commit as its version. It declares
`authentication: {"required": true, "schemes": ["bearer"]}` and generates its
tools from the same registrations as `tools/list`. The card uses a short public
cache lifetime.

Sources: [Smithery publishing](https://smithery.ai/docs/build/publish) and
[configuration transport](https://smithery.ai/docs/build/session-config).

## SDK and transport

| Choice | What |
|---|---|
| Handler | `createMcpHandler` from `agents/mcp/server` |
| Server | `McpServer` from `@modelcontextprotocol/server` 2.0 |
| Transport | Streamable HTTP (`POST /mcp`) |
| State | Stateless. No Durable Object. |

`McpAgent` is deprecated and feature-frozen; it exists for sessionful servers
that need Durable Object state. These tools are proxies: each call hits the
public rank API, policy-check API, or the static JSON export and returns that
body plus the origin URL. There is nothing to persist.

Read (2026-09-18):

- https://developers.cloudflare.com/agents/model-context-protocol/apis/handler-api/
- https://developers.cloudflare.com/agents/model-context-protocol/guides/remote-mcp-server/
- https://developers.cloudflare.com/agents/model-context-protocol/apis/agent-api/

## Route

Workers routes `api.modelspec.dev/mcp*` and
`api.modelspec.dev/.well-known/mcp/server-card.json` on zone `modelspec.dev`
belong to this Worker. The rank Worker already owns `api.modelspec.dev/*`;
the more specific patterns win.
The CI token can edit Workers routes and cannot create DNS, so there is no
new hostname.

## Tools

Successful calls pass through the origin. Null on a card means not researched.

| Tool | Origin |
|---|---|
| `rank` | `POST https://api.modelspec.dev/v1/rank` |
| `model_info` | `GET https://modelspec.dev/api/models/<id>.json` |
| `list_use_cases` | `GET https://modelspec.dev/api/rank/profiles.json` |
| `policy_check` | `POST https://api.modelspec.dev/v1/policy-check` |
| `decide` | `POST https://api.modelspec.dev/v1/decide` |
| `compare_models` | `POST https://api.modelspec.dev/v1/compare-models` |
| `hardware_fit` | `POST https://api.modelspec.dev/v1/hardware-fit` |
| `vocab` | `GET https://modelspec.dev/api/decision/vocabulary.json` |
| `feedback` | `POST https://api.modelspec.dev/v1/feedback` (no key; `client` is always `mcp`; the caller's address is forwarded only for the rate limit) |

`rank`, `policy_check`, `decide`, `compare_models`, and `hardware_fit` use the `RANK` service binding because a
same-zone Worker fetch to the public API hostname reaches the zone origin and
returns 522. All five forward the key as `Authorization: Bearer <key>`.
The API validates presented keys and returns its auth/payment errors unchanged.

MCP accepts either `Authorization: Bearer <key>` or `x-api-key: <key>`.
If both headers are present, their keys must agree; conflicting credentials
return HTTP 400 with a JSON-RPC error. Keys never appear in logs or error
messages.

All data tools require a ModelSpec key, including when
`MCP_REQUIRE_API_KEY="false"`. Missing or malformed credentials return a
401 `missing_api_key` refusal before any origin call. This includes `rank`,
`policy_check`, `decide`, `compare_models`, `hardware_fit`, `vocab`,
`model_info` and `list_use_cases`. `initialize` and `tools/list` remain public.
Feedback stays keyless and carries no model data. Use an existing key, or see
[pricing](https://modelspec.dev/pricing/) for availability.

`decide` accepts the decision spec defined by
[`docs/decision-contract.md`](../docs/decision-contract.md). Its MCP input
schema comes from the generated `docs/decision-contract.schema.json`, so the
API and MCP contracts cannot drift. Read `vocab` first for valid facet ids.
Use `where` for Musts that exclude and `optimize.weights` for Prefers that
rank without excluding. Unknown capability values appear in `may_qualify`.
Pin `snapshot` to reproduce a decision.

`compare_models` accepts only `{models: ["lab/a", "lab/b"]}`, with 2 to 4
distinct catalogue ids. It returns the current snapshot's sourced facts,
offerings and evidence in caller order. It does not rank or choose a winner.
Unknown values stay null, and `omitted` counts removed records. The entire MCP
text stays within 16 KB. An oversized origin response becomes a compact
`response_too_large` tool error and returns no comparison data. This named
model comparison does not change the snapshot comparison at `/v1/compare`.

`hardware_fit` accepts `model`, `sku`, `device_count`, `memory`, `runtime`,
`quantisation`, `batch` and `context`. Memory is an optional override in decimal
GB per device. Omitted or null inputs reach the API and return `undetermined`
when they prevent assessment. Unknown SKU or quantisation identifiers also
reach the API. The tool preserves the endpoint's complete answer and citations.
A `measured` answer cites the exact run. An `estimated` answer gives
`estimated_fit: likely|unlikely`, a memory margin, the formula, inputs and
assumptions. An estimate never proves fit or contains `fits: true`.

## Client config

Run `modelspec setup mcp --client claude-code` or
`modelspec setup mcp --client claude-desktop` for the client's native snippet.
Claude Code:

```json
{
  "mcpServers": {
    "modelspec": {
      "type": "http",
      "url": "https://api.modelspec.dev/mcp",
      "headers": { "Authorization": "Bearer <API_KEY>" }
    }
  }
}
```

Claude Desktop uses the `mcp-remote` stdio bridge and requires Node.js/npx:

```json
{
  "mcpServers": {
    "modelspec": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://api.modelspec.dev/mcp",
               "--header", "Authorization:${MODELSPEC_AUTH_HEADER}"],
      "env": {"MODELSPEC_AUTH_HEADER": "Bearer <MODELSPEC_API_KEY>"}
    }
  }
}
```

macOS GUI apps do not inherit your shell environment. Explicitly replace the
placeholder in the `env` block with your key, retaining `Bearer `; that stores
the key in this config. The CLI's setup command writes the placeholder and
never copies a saved or environment key into the config. The `env` block and
header form follow the [mcp-remote documentation](https://github.com/punkpeye/mcp-remote#custom-headers).

## Local

```bash
npm install
npm test
npm run typecheck
npx wrangler@4.134.0 dev --local --var BUILD_COMMIT:dev
```

Deploy is `.github/workflows/mcp.yml` on push to `main` only. Do not deploy
from a laptop.
