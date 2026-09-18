/** Fetch an origin and return exactly what it answered, plus its URL. */

export const USER_AGENT =
  "modelspec-mcp/1.0 (+https://github.com/turbobeest/modelspec)";

export type OriginEnvelope = {
  origin: string;
  status: number;
  body: unknown;
};

export function asToolResult(envelope: OriginEnvelope) {
  return {
    content: [{ type: "text" as const, text: JSON.stringify(envelope) }],
    isError: envelope.status === 0 || envelope.status >= 400,
  };
}

export async function fetchOrigin(
  origin: string,
  init: RequestInit = {},
): Promise<OriginEnvelope> {
  const headers = new Headers(init.headers);
  if (!headers.has("user-agent")) headers.set("user-agent", USER_AGENT);
  if (!headers.has("accept")) headers.set("accept", "application/json");
  try {
    const response = await fetch(origin, {
      ...init,
      headers,
      signal: init.signal ?? AbortSignal.timeout(30_000),
    });
    const text = await response.text();
    let body: unknown = text;
    try {
      body = JSON.parse(text) as unknown;
    } catch {
      // Pass non-JSON through as text. Do not reshape it.
    }
    return { origin, status: response.status, body };
  } catch (err) {
    return {
      origin,
      status: 0,
      body: {
        error: {
          code: "origin_unreachable",
          message: err instanceof Error ? err.message : String(err),
        },
      },
    };
  }
}

export function incomingAuthorization(request: Request | undefined): string | undefined {
  if (!request) return undefined;
  return (
    request.headers.get("Authorization") ??
    request.headers.get("authorization") ??
    undefined
  );
}

/**
 * Catalogue ids are `provider/slug`. Reject anything that would not be a
 * path under /api/models/. A refused id is not fetched.
 */
export function modelCardUrl(
  exportOrigin: string,
  modelId: string,
): { origin: string } | { error: string } {
  const id = modelId.trim();
  if (
    !id ||
    id.includes("..") ||
    id.includes("\\") ||
    id.startsWith("/") ||
    /[a-z]+:\/\//i.test(id)
  ) {
    return { error: "model_id must be a catalogue id such as openai/gpt-5-6" };
  }
  const base = exportOrigin.replace(/\/$/, "");
  return { origin: `${base}/api/models/${id}.json` };
}
