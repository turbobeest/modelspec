# ModelSpec remote MCP server

Read-only MCP tools over the ModelSpec catalogue. Decision tools require an
API key. The site stays on Cloudflare Pages; this Worker only answers
`https://api.modelspec.dev/mcp`.

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

Workers route `api.modelspec.dev/mcp*` on zone `modelspec.dev`. The rank
Worker already owns `api.modelspec.dev/*`; the more specific pattern wins.
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
| `vocab` | `GET https://modelspec.dev/api/decision/vocabulary.json` |
| `feedback` | `POST https://api.modelspec.dev/v1/feedback` (no key; `client` is always `mcp`; the caller's address is forwarded only for the rate limit) |

`rank`, `policy_check`, and `decide` use the `RANK` service binding because a
same-zone Worker fetch to the public API hostname reaches the zone origin and
returns 522. All three forward the client's `Authorization: Bearer <key>` header.
The API validates presented keys and returns its auth/payment errors unchanged.

`MCP_REQUIRE_API_KEY` defaults to requiring a key, including when unset. Only
explicit `"false"` permits anonymous decision calls. With the default, `rank`,
`policy_check` and `decide` return a 401 `missing_api_key` tool error before
contacting the API when a Bearer credential is absent or malformed. This guard
is necessary because the API can serve keyless requests while its
`ACCESS_ENFORCED` flag is off. That API flag, `BILLING_ENABLED` and
`X402_ENABLED` are unchanged. Catalogue and vocabulary reads and feedback
remain keyless; they do not produce decisions.

`decide` accepts the decision spec defined by
[`docs/decision-contract.md`](../docs/decision-contract.md). Its MCP input
schema comes from the generated `docs/decision-contract.schema.json`, so the
API and MCP contracts cannot drift. Read `vocab` first for valid facet ids.
Use `where` for Musts that exclude and `optimize.weights` for Prefers that
rank without excluding. Unknown capability values appear in `may_qualify`.
Pin `snapshot` to reproduce a decision.

## Client config

Claude Code / Claude Desktop:

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

## Local

```bash
npm install
npm test
npm run typecheck
npx wrangler@4.134.0 dev --local --var BUILD_COMMIT:dev
```

Deploy is `.github/workflows/mcp.yml` on push to `main` only. Do not deploy
from a laptop.
