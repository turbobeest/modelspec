// benchgraph graph Worker (MODEL-9). Read-only router in front of the FalkorDB
// query container. It is scoped to /graph/* and is NOT the MODEL-3 site/API
// Worker: the sites stay static on Pages.
import { Container, ContainerProxy, getContainer } from "@cloudflare/containers";
import { EXPORT_HOST, blockOutbound, serveExport } from "./export.js";
import { rollStaleContainer, staleHealth } from "./rollout.js";

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
  defaultPort = 8080;
  // Idle containers stop; the next request cold-starts and reloads the export.
  // A deploy does not wait for that: see `fetch` below.
  sleepAfter = "15m";

  constructor(ctx, env) {
    super(ctx, env);
    // BUILD_COMMIT is the deployed version (`wrangler deploy --var`). It is read
    // when the container *starts*, so a container still running from an earlier
    // deploy reports the earlier value — which is what makes staleness visible.
    this.envVars = {
      GRAPH_EXPORT_URL: env.GRAPH_EXPORT_URL,
      BUILD_COMMIT: env.BUILD_COMMIT ?? "",
    };
  }

  // A deploy replaces this class's code but leaves a running container alone, so
  // without this every request after a deploy is answered by the old image.
  // Destroying it here means the `super.fetch` below starts a fresh instance on
  // the deployed image, with the deployed envVars. Once per BUILD_COMMIT: see
  // rollStaleContainer.
  async fetch(request) {
    await rollStaleContainer({
      kv: this.ctx.storage.kv,
      container: this.ctx.container,
      want: this.env.BUILD_COMMIT,
      log: (message) => console.log(message),
    });
    return super.fetch(request);
  }

  // Container stdout/stderr goes to the dashboard Container logs page, not to
  // `wrangler tail`. These hooks put the lifecycle on the Worker's own log
  // stream, where tail does see them. Messages only: no env, no stack.
  onStart() {
    console.log("GraphContainer started");
  }

  onStop({ exitCode, reason } = {}) {
    console.log(`GraphContainer stopped: exitCode=${exitCode} reason=${reason}`);
  }

  onError(error) {
    const detail = error instanceof Error ? `${error.name}: ${error.message}` : String(error);
    console.error(`GraphContainer error: ${detail}`);
    throw error;
  }
}

// Assigned, never written as `static` class fields inside the class body.
// `Container` declares `outboundByHost` and `outbound` as static *accessor
// pairs* whose setters are the only writers of the module-level registries that
// `ContainerProxy` reads (@cloudflare/containers 0.3.7,
// `dist/lib/container.js:272-296`). A native `static` field defines an own
// property on the subclass instead of invoking the inherited setter
// (cloudflare/containers#247), so the registry stayed empty while
// `ctor.outboundByHost` still read back the shadowing object. That is the whole
// 530: `getHostsToIntercept()` armed interception, `ContainerProxy` found no
// handler for the class, and fell through to `return fetch(request)` — a real
// Worker subrequest for `graph-export.internal`, which does not resolve
// publicly, so the runtime answered with an empty-bodied 530 while the tail
// event's outcome stayed `Ok`. Assignment invokes the setter.
GraphContainer.outboundByHost = { [EXPORT_HOST]: serveExport };
// Deny-by-default for every other HTTP host: refused and named in the log
// instead of leaving for the public internet. This also promotes the container
// to intercept-all HTTP, so if the line above ever stops registering, the
// failure shows up as `outbound blocked: GET graph-export.internal/...` rather
// than as another unexplained 530. `enableInternet` stays at its default: 0.3.7
// still carries "TODO: hopefully, enableInternet can be false in a future where
// we enable DNS and TLS paths", and the container has to resolve EXPORT_HOST.
GraphContainer.outbound = blockOutbound;

function json(status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
}

// /graph/health is the one route whose body the Worker reads, because it is the
// deploy's assertion point: a 200 from it must mean "the deployed image is
// answering". Every other route streams through untouched; they are protected by
// the roll in GraphContainer.fetch, not by a body check.
async function gateHealth(response, want, headOnly) {
  const text = await response.text();
  let body = null;
  try {
    body = JSON.parse(text);
  } catch {
    body = null;
  }
  const stale = staleHealth(body, want);
  const status = stale ? 503 : response.status;
  const payload = stale ? JSON.stringify({ ...(body ?? {}), ...stale }) : text;
  return new Response(headOnly ? null : payload, {
    status,
    headers: {
      "content-type": "application/json",
      "cache-control": stale ? "no-store" : response.headers.get("cache-control") ?? "no-store",
    },
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
    const isHealth = match[1] === "health";
    // A HEAD of health is answered from a GET upstream, so the version gate has
    // a body to read; the client still gets no body back.
    const method = isHealth ? "GET" : request.method;
    const container = getContainer(env.GRAPH, "benchgraph-graph");
    const response = await container.fetch(new Request(upstream, { method }));
    if (!isHealth) return response;
    return gateHealth(response, env.BUILD_COMMIT, request.method === "HEAD");
  },
};
