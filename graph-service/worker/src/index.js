// benchgraph graph Worker (MODEL-9). Read-only router in front of the FalkorDB
// query container. It is scoped to /graph/* and is NOT the MODEL-3 site/API
// Worker: the sites stay static on Pages.
import { Container, ContainerProxy, getContainer } from "@cloudflare/containers";
import { EXPORT_HOST, serveExport } from "./export.js";

// Required for outbound interception: the container's requests to EXPORT_HOST
// are served from the EXPORTS R2 binding (see export.js).
export { ContainerProxy };

// Must match graph-service/service.py ALLOWED (tests/test_benchgraph_graph.py checks).
const ALLOWED = new Set([
  "health",
  "manifest",
  "benchmarks_still_separating",
]);

const MAX_QUERY_LENGTH = 512;

export class GraphContainer extends Container {
  static outboundByHost = { [EXPORT_HOST]: serveExport };
  defaultPort = 8080;
  // Idle containers stop; the next request cold-starts and reloads the export.
  sleepAfter = "15m";

  constructor(ctx, env) {
    super(ctx, env);
    this.envVars = { GRAPH_EXPORT_URL: env.GRAPH_EXPORT_URL };
  }
}

function json(status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
}

export default {
  async fetch(request, env) {
    if (request.method !== "GET" && request.method !== "HEAD") {
      return json(405, { error: "read-only" });
    }
    const url = new URL(request.url);
    const match = url.pathname.match(/^\/graph\/([a-z_]+)$/);
    if (!match || !ALLOWED.has(match[1])) {
      return json(404, { error: "unknown route", allowed: [...ALLOWED] });
    }
    if (url.search.length > MAX_QUERY_LENGTH) {
      return json(400, { error: "query string too long" });
    }
    // Forward only the route name and query string: no body, no client headers.
    const upstream = new URL(`http://graph/graph/${match[1]}`);
    upstream.search = url.search;
    const container = getContainer(env.GRAPH, "benchgraph-graph");
    return container.fetch(new Request(upstream, { method: request.method }));
  },
};
