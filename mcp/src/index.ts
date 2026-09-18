import { mcpHandler } from "./server";

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
  return mcpHandler(env)(withMcpPath(request), env, ctx);
}

export default {
  fetch: workerFetch,
} satisfies ExportedHandler<Env>;
