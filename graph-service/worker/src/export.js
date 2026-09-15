// Serves the graph export to the container from the EXPORTS R2 binding
// (MODEL-9). No imports, so tests can run it under plain node.
//
// The container's outbound calls to EXPORT_HOST are intercepted
// (GraphContainer.outboundByHost) and answered here, so loading the export
// never depends on the public custom domain, which the container could not
// load from in production.

// Must match GRAPH_EXPORT_URL's host in wrangler.jsonc.
export const EXPORT_HOST = "graph-export.internal";
const EXPORT_PATH = /^\/benchgraph-graph\/latest\/(manifest|nodes|edges)\.json$/;

// Read-only: GET of exactly the three export files under latest/. No listing.
// Logs every intercepted request. The container's own stdout does not reach
// `wrangler tail`, so this line is the proof that outbound interception fired
// at all: no line means the container never asked for the export.
export async function serveExport(request, env) {
  const url = new URL(request.url);
  const response = await handleExport(request, env, url);
  console.log(`export ${request.method} ${url.pathname} -> ${response.status}`);
  return response;
}

async function handleExport(request, env, url) {
  if (request.method !== "GET") return new Response("read-only", { status: 405 });
  if (!EXPORT_PATH.test(url.pathname)) return new Response("not found", { status: 404 });
  const object = await env.EXPORTS.get(url.pathname.slice(1));
  if (!object) return new Response("not found", { status: 404 });
  return new Response(object.body, { headers: { "content-type": "application/json" } });
}
