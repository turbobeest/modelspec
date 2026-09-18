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

All four pass through the origin. Null on a card means not researched.

| Tool | Origin |
|---|---|
| `rank` | `POST https://api.modelspec.dev/v1/rank` |
| `model_info` | `GET https://modelspec.dev/api/models/<id>.json` |
| `list_use_cases` | `GET https://modelspec.dev/api/rank/profiles.json` |
| `policy_check` | `POST https://api.modelspec.dev/v1/policy-check` |

`policy_check` forwards an `Authorization` header if the MCP client sent one.
Without a key the origin answers the free tier.

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
