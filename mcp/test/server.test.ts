import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { workerFetch } from "../src/index";
import { USER_AGENT } from "../src/origin";
import { TOOL_NAMES } from "../src/server";

const ENV: Env = {
  EXPORT_ORIGIN: "https://modelspec.dev",
  RANK_API_ORIGIN: "https://api.modelspec.dev",
  BUILD_COMMIT: "test-commit-sha",
};

function testCtx(): ExecutionContext {
  return {
    waitUntil(promise: Promise<unknown>) {
      void promise;
    },
    passThroughOnException() {},
    props: {},
  };
}

function parseMcpBody(text: string): unknown {
  const trimmed = text.trim();
  if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
    return JSON.parse(trimmed) as unknown;
  }
  const datas: unknown[] = [];
  for (const line of trimmed.split("\n")) {
    if (!line.startsWith("data:")) continue;
    const payload = line.slice(5).trim();
    if (!payload || payload === "[DONE]") continue;
    datas.push(JSON.parse(payload) as unknown);
  }
  if (datas.length === 1) return datas[0];
  if (datas.length > 1) return datas;
  throw new Error(`unreadable MCP body: ${trimmed.slice(0, 200)}`);
}

async function rpc(
  method: string,
  params: Record<string, unknown>,
  id = 1,
  headers: Record<string, string> = {},
): Promise<{ status: number; payload: Record<string, unknown> }> {
  const response = await workerFetch(
    new Request("http://localhost/mcp", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        accept: "application/json, text/event-stream",
        host: "localhost",
        ...headers,
      },
      body: JSON.stringify({ jsonrpc: "2.0", id, method, params }),
    }),
    ENV,
    testCtx(),
  );
  const text = await response.text();
  if (!text.trim().startsWith("{") && !text.includes("jsonrpc")) {
    throw new Error(`HTTP ${response.status} unreadable MCP body: ${text.slice(0, 500)}`);
  }
  const parsed = parseMcpBody(text);
  if (typeof parsed === "object" && parsed && "error" in parsed && !("result" in parsed)) {
    throw new Error(`HTTP ${response.status} JSON-RPC error: ${JSON.stringify(parsed)}`);
  }
  if (typeof parsed === "object" && parsed && !("result" in (parsed as object))) {
    throw new Error(`HTTP ${response.status} no result: ${JSON.stringify(parsed).slice(0, 800)}`);
  }
  if (typeof parsed !== "object" || parsed === null) {
    throw new Error(`expected JSON-RPC object, got ${text.slice(0, 200)}`);
  }
  return { status: response.status, payload: parsed as Record<string, unknown> };
}

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

function envelopeFromCall(payload: Record<string, unknown>): {
  origin: string;
  status: number;
  body: unknown;
} {
  const result = payload.result as { content: Array<{ text: string }>; isError?: boolean };
  return JSON.parse(result.content[0].text) as {
    origin: string;
    status: number;
    body: unknown;
  };
}

describe("modelspec MCP worker", () => {
  const originFetch = vi.fn();

  beforeEach(() => {
    originFetch.mockReset();
    vi.stubGlobal("fetch", originFetch);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("tools/list returns the four tools with object input schemas", async () => {
    const listed = await rpc("tools/list", {});
    const result = listed.payload.result as {
      tools: Array<{ name: string; inputSchema: { type?: string } }>;
    };
    expect(result.tools.map((tool) => tool.name).sort()).toEqual(
      [...TOOL_NAMES].sort(),
    );
    expect(result.tools).toHaveLength(4);
    for (const tool of result.tools) {
      expect(tool.inputSchema).toBeTruthy();
      expect(tool.inputSchema.type ?? "object").toBe("object");
    }
  });

  it("initialize reports BUILD_COMMIT as serverInfo.version", async () => {
    const { payload } = await rpc("initialize", {
      protocolVersion: "2025-03-26",
      capabilities: {},
      clientInfo: { name: "vitest", version: "0" },
    });
    const result = payload.result as { serverInfo: { name: string; version: string } };
    expect(result.serverInfo.name).toBe("modelspec");
    expect(result.serverInfo.version).toBe("test-commit-sha");
  });

  it("rank happy path proxies the origin JSON and URL", async () => {
    const originBody = { result: [{ model_id: "deepseek/deepseek-v3-2", score: 1 }] };
    originFetch.mockResolvedValueOnce(jsonResponse(200, originBody));
    const { payload } = await rpc("tools/call", {
      name: "rank",
      arguments: { use_case: "coding", limit: 1 },
    });
    const envelope = envelopeFromCall(payload);
    expect(envelope.origin).toBe("https://api.modelspec.dev/v1/rank");
    expect(envelope.status).toBe(200);
    expect(envelope.body).toEqual(originBody);
    expect(originFetch).toHaveBeenCalledOnce();
    const [url, init] = originFetch.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("https://api.modelspec.dev/v1/rank");
    expect(init.method).toBe("POST");
    expect(JSON.parse(String(init.body))).toEqual({ use_case: "coding", limit: 1 });
    const headers = new Headers(init.headers);
    expect(headers.get("user-agent")).toBe(USER_AGENT);
  });

  it("rank error path returns the origin 400", async () => {
    const originBody = { error: { code: "unknown_use_case" } };
    originFetch.mockResolvedValueOnce(jsonResponse(400, originBody));
    const { payload } = await rpc("tools/call", {
      name: "rank",
      arguments: { use_case: "not_a_use_case" },
    });
    const envelope = envelopeFromCall(payload);
    expect(envelope.status).toBe(400);
    expect(envelope.body).toEqual(originBody);
    expect((payload.result as { isError?: boolean }).isError).toBe(true);
  });

  it("model_info happy path reads /api/models/<id>.json", async () => {
    const originBody = { card: { identity: { name: "DeepSeek V3.2" } } };
    originFetch.mockResolvedValueOnce(jsonResponse(200, originBody));
    const { payload } = await rpc("tools/call", {
      name: "model_info",
      arguments: { model_id: "deepseek/deepseek-v3-2" },
    });
    const envelope = envelopeFromCall(payload);
    expect(envelope.origin).toBe(
      "https://modelspec.dev/api/models/deepseek/deepseek-v3-2.json",
    );
    expect(envelope.status).toBe(200);
    expect(envelope.body).toEqual(originBody);
  });

  it("model_info error path returns the origin 404", async () => {
    originFetch.mockResolvedValueOnce(jsonResponse(404, { error: "not found" }));
    const { payload } = await rpc("tools/call", {
      name: "model_info",
      arguments: { model_id: "missing/model" },
    });
    const envelope = envelopeFromCall(payload);
    expect(envelope.status).toBe(404);
    expect((payload.result as { isError?: boolean }).isError).toBe(true);
  });

  it("list_use_cases happy path reads profiles.json", async () => {
    const originBody = { profiles: { coding: {} } };
    originFetch.mockResolvedValueOnce(jsonResponse(200, originBody));
    const { payload } = await rpc("tools/call", {
      name: "list_use_cases",
      arguments: {},
    });
    const envelope = envelopeFromCall(payload);
    expect(envelope.origin).toBe("https://modelspec.dev/api/rank/profiles.json");
    expect(envelope.body).toEqual(originBody);
  });

  it("list_use_cases error path surfaces an unreachable origin", async () => {
    originFetch.mockRejectedValueOnce(new Error("network down"));
    const { payload } = await rpc("tools/call", {
      name: "list_use_cases",
      arguments: {},
    });
    const envelope = envelopeFromCall(payload);
    expect(envelope.origin).toBe("https://modelspec.dev/api/rank/profiles.json");
    expect(envelope.status).toBe(0);
    expect((envelope.body as { error: { code: string } }).error.code).toBe(
      "origin_unreachable",
    );
    expect((payload.result as { isError?: boolean }).isError).toBe(true);
  });

  it("policy_check happy path proxies the origin JSON", async () => {
    const originBody = { result: [{ verdict: "undetermined" }] };
    originFetch.mockResolvedValueOnce(jsonResponse(200, originBody));
    const { payload } = await rpc("tools/call", {
      name: "policy_check",
      arguments: { policy: { origin: { permitted_countries: ["US"] } }, limit: 1 },
    });
    const envelope = envelopeFromCall(payload);
    expect(envelope.origin).toBe("https://api.modelspec.dev/v1/policy-check");
    expect(envelope.status).toBe(200);
    expect(envelope.body).toEqual(originBody);
  });

  it("policy_check error path returns the origin 400", async () => {
    const originBody = { error: { code: "invalid_request" } };
    originFetch.mockResolvedValueOnce(jsonResponse(400, originBody));
    const { payload } = await rpc("tools/call", {
      name: "policy_check",
      arguments: { policy: {} },
    });
    const envelope = envelopeFromCall(payload);
    expect(envelope.status).toBe(400);
    expect(envelope.body).toEqual(originBody);
  });

  it("policy_check forwards a client Authorization header", async () => {
    originFetch.mockResolvedValueOnce(jsonResponse(200, { ok: true }));
    await rpc(
      "tools/call",
      {
        name: "policy_check",
        arguments: { policy: { origin: { permitted_countries: ["US"] } } },
      },
      1,
      { authorization: "Bearer test_key" },
    );
    const init = originFetch.mock.calls[0][1] as RequestInit;
    expect(new Headers(init.headers).get("authorization")).toBe("Bearer test_key");
  });
});
