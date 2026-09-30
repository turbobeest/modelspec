# ModelSpec remote MCP server

Read-only MCP tools over the public ModelSpec catalogue. No key. The site
stays on Cloudflare Pages; this Worker only answers
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

All seven pass through the origin. Null on a card means not researched.

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
returns 522. `policy_check` and `decide` forward an `Authorization` header if
the MCP client sent one. Without a key the origin answers the free tier.

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
      "url": "https://api.modelspec.dev/mcp"
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
