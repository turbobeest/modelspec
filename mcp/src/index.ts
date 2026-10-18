import { mcpHandler, serverCard } from "./server";

async function conflictingKeys(request: Request): Promise<Response> {
  let id: string | number | null = null;
  try {
    const body: unknown = await request.clone().json();
    if (typeof body === "object" && body !== null && "id" in body &&
      (typeof body.id === "string" || typeof body.id === "number")) id = body.id;
  } catch {
    // A transport-level rejection can precede a valid JSON-RPC request.
  }
  return Response.json({
    jsonrpc: "2.0", id,
    error: { code: -32600, message: "Authorization and x-api-key credentials must match." },
  }, { status: 400, headers: { "cache-control": "no-store" } });
}

async function normalizeAuthorization(request: Request): Promise<Request | Response> {
  const authorization = request.headers.get("authorization");
  const apiKey = request.headers.get("x-api-key");
  const bearerKey = authorization?.match(/^Bearer +(\S+)$/i)?.[1];
  if (apiKey !== null && authorization !== null && apiKey !== bearerKey) {
    return conflictingKeys(request);
  }
  const key = apiKey ?? bearerKey;
  if (key === undefined) return request;
  const headers = new Headers(request.headers);
  headers.set("authorization", `Bearer ${key}`);
  headers.delete("x-api-key");
  return new Request(request, { headers });
}

function withMcpPath(request: Request): Request {
  const url = new URL(request.url);
  if (url.pathname !== "/mcp/") {
    return request;
  }
  url.pathname = "/mcp";
  return new Request(url, request);
}

export async function workerFetch(
  request: Request,
  env: Env,
  ctx: ExecutionContext,
): Promise<Response> {
  if (new URL(request.url).pathname === "/.well-known/mcp/server-card.json") {
    if (request.method !== "GET") {
      return new Response(null, { status: 405, headers: { allow: "GET" } });
    }
    return Response.json(serverCard(env), { headers: {
      "cache-control": "public, max-age=300",
      "access-control-allow-origin": "*",
      "access-control-allow-methods": "GET",
      "access-control-allow-headers": "Content-Type",
    } });
  }
  const normalized = await normalizeAuthorization(request);
  if (normalized instanceof Response) return normalized;
  return mcpHandler(env)(withMcpPath(normalized), env, ctx);
}

export default {
  fetch: workerFetch,
} satisfies ExportedHandler<Env>;
