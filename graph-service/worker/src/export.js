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

function encode(body) {
  return typeof body === "string" ? new TextEncoder().encode(body) : new Uint8Array(body);
}

// Read-only: GET of exactly the three export files under latest/. No listing.
// Logs status and byte count for every intercepted request. The container's own
// stdout does not reach `wrangler tail`, so this line is the proof that outbound
// interception fired and that bytes were actually produced: no line means the
// container never asked for the export (or the request never matched this
// handler and fell through), and `-> 200 0B` would mean it matched but produced
// nothing.
export async function serveExport(request, env) {
  const url = new URL(request.url);
  let result;
  try {
    result = await readExport(request, env, url);
  } catch (error) {
    // An exception escaping here reaches the container as an opaque failure with
    // a tail outcome that still looks fine. Turn it into a response we can read.
    const detail = error instanceof Error ? `${error.name}: ${error.message}` : String(error);
    console.error(`export ${request.method} ${url.pathname} failed: ${detail}`);
    result = { status: 502, body: "export unavailable", type: "text/plain" };
  }
  const bytes = encode(result.body);
  console.log(`export ${request.method} ${url.pathname} -> ${result.status} ${bytes.byteLength}B`);
  // Buffered, with an explicit content-length: the response crosses the outbound
  // interception hop into the container's network namespace, so it is handed a
  // complete body rather than an R2 stream this handler has already returned
  // from. The largest file is a few MB.
  return new Response(bytes, {
    status: result.status,
    headers: {
      "content-type": result.type,
      "content-length": String(bytes.byteLength),
      "cache-control": "no-store",
    },
  });
}

async function readExport(request, env, url) {
  if (request.method !== "GET") return { status: 405, body: "read-only", type: "text/plain" };
  if (!EXPORT_PATH.test(url.pathname)) return { status: 404, body: "not found", type: "text/plain" };
  const object = await env.EXPORTS.get(url.pathname.slice(1));
  if (!object) return { status: 404, body: "not found", type: "text/plain" };
  return { status: 200, body: await object.arrayBuffer(), type: "application/json" };
}

// Catch-all for every other host the container asks for over HTTP.
//
// Without it the library stays in per-host interception mode, and a request that
// matches no handler falls through to `fetch(request)` inside the Worker. For a
// hostname that does not resolve publicly — which EXPORT_HOST is, by design —
// that subrequest comes back as an empty-bodied 530 while the Worker event's
// outcome is still "Ok", which is exactly what the container reported
// (`HTTPError: HTTP Error 530:`) and is indistinguishable from a delivery
// failure. Registering this promotes the container to intercept-all HTTP
// (Container.needsCatchAllInterception in @cloudflare/containers 0.3.7), so an
// unmatched host is named in the log and refused instead of silently leaving for
// the public internet. HTTPS is not intercepted (interceptHttps is false), and
// the container makes no other HTTP calls.
export async function blockOutbound(request) {
  const url = new URL(request.url);
  console.error(`outbound blocked: ${request.method} ${url.host}${url.pathname}`);
  return new Response("outbound host not allowed", {
    status: 502,
    headers: { "content-type": "text/plain", "cache-control": "no-store" },
  });
}
