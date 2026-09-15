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
export async function serveExport(request, env) {
  if (request.method !== "GET") return new Response("read-only", { status: 405 });
  const url = new URL(request.url);
  if (!EXPORT_PATH.test(url.pathname)) return new Response("not found", { status: 404 });
  const object = await env.EXPORTS.get(url.pathname.slice(1));
  if (!object) return new Response("not found", { status: 404 });
  return new Response(object.body, { headers: { "content-type": "application/json" } });
}
