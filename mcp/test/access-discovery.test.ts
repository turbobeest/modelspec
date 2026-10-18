import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { z } from "zod";

import { workerFetch } from "../src/index";

const ENV: Env = {
  EXPORT_ORIGIN: "https://modelspec.dev",
  RANK_API_ORIGIN: "https://api.modelspec.dev",
  BUILD_COMMIT: "model-403-test-commit",
};
const context: ExecutionContext = {
  waitUntil(promise) { void promise; },
  passThroughOnException() {},
  props: {},
};
const toolResult = z.object({ result: z.object({
  content: z.array(z.object({ type: z.literal("text"), text: z.string() })).min(1),
  isError: z.boolean().optional(),
}) });
const envelope = z.object({ status: z.number(), body: z.unknown() });
const tool = z.object({
  name: z.string(), description: z.string(), inputSchema: z.record(z.string(), z.unknown()),
});
const serverInfo = z.object({ name: z.string(), version: z.string() });
const initializeParams = {
  protocolVersion: "2025-03-26", capabilities: {},
  clientInfo: { name: "model-403-test", version: "1" },
};
const rankCall = { name: "rank", arguments: { use_case: "coding" } };
const dataCalls = [
  rankCall,
  { name: "model_info", arguments: { model_id: "lab/model" } },
  { name: "list_use_cases", arguments: {} },
  { name: "policy_check", arguments: { policy: {} } },
  { name: "decide", arguments: { spec_version: 1, optimize: { min: "offering.cost_per_task" } } },
  { name: "compare_models", arguments: { models: ["lab/one", "lab/two"] } },
  { name: "hardware_fit", arguments: {} },
  { name: "vocab", arguments: {} },
];

async function rpc({
  method = "tools/call", params = rankCall, headers = {}, env = ENV, path = "/mcp",
}: {
  method?: string; params?: unknown; headers?: Record<string, string>; env?: Env; path?: string;
} = {}) {
  const response = await workerFetch(new Request(`http://localhost${path}`, {
    method: "POST",
    headers: { host: "localhost", "content-type": "application/json", accept: "application/json, text/event-stream", ...headers },
    body: JSON.stringify({ jsonrpc: "2.0", id: 403, method, params }),
  }), env, context);
  const text = await response.text();
  const json = text.trim().startsWith("{") ? text : text.split("\n")
    .find(line => line.startsWith("data:"))?.slice(5);
  if (json === undefined) throw new Error(`No JSON-RPC response at HTTP ${response.status}`);
  const payload: unknown = JSON.parse(json);
  return { response, payload, text };
}

function readEnvelope(payload: unknown) {
  const result = toolResult.parse(payload).result;
  const first = result.content[0];
  if (first === undefined) throw new Error("No tool content");
  return { result, value: envelope.parse(JSON.parse(first.text)) };
}

describe("MCP API-key headers and discovery", () => {
  const originFetch = vi.fn<typeof fetch>();
  const via = { fetch: vi.fn<typeof fetch>() };

  beforeEach(() => {
    originFetch.mockReset().mockImplementation(async () => Response.json({ result: [] }));
    via.fetch.mockReset().mockImplementation(async () => Response.json({ result: [] }));
    vi.stubGlobal("fetch", originFetch);
  });
  afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks(); });

  it.each([
    { label: "x-api-key alone", headers: { "x-api-key": "alias_test_secret" } },
    { label: "Bearer alone", headers: { authorization: "Bearer alias_test_secret" } },
    { label: "agreeing headers", headers: { authorization: "Bearer alias_test_secret", "x-api-key": "alias_test_secret" } },
    { label: "case-insensitive header and scheme", headers: { Authorization: "bEaReR alias_test_secret", "X-API-Key": "alias_test_secret" } },
  ])("$label succeeds and sends only normalized Bearer to the origin", async ({ headers }) => {
    for (const path of ["/mcp", "/mcp/"]) {
      const { response, payload } = await rpc({ headers, path, env: { ...ENV, RANK: via } });
      expect(response.status).toBe(200);
      expect(readEnvelope(payload).value.status).toBe(200);
    }
    expect(via.fetch).toHaveBeenCalledTimes(2);
    for (const [, init] of via.fetch.mock.calls) {
      const forwarded = new Headers(init?.headers);
      expect(forwarded.get("authorization")).toBe("Bearer alias_test_secret");
      expect(forwarded.has("x-api-key")).toBe(false);
    }
    expect(originFetch).not.toHaveBeenCalled();
  });

  it.each([
    { authorization: "Bearer bearer_secret", "x-api-key": "alias_secret" },
    { authorization: "Basic bearer_secret", "x-api-key": "alias_secret" },
    { authorization: "", "x-api-key": "alias_secret" },
    { authorization: "Bearer bearer_secret", "x-api-key": "" },
  ])("conflicting headers return HTTP 400 and a clear JSON-RPC error", async headers => {
    const { response, payload, text } = await rpc({ headers });
    expect(response.status).toBe(400);
    expect(response.headers.get("content-type")).toContain("application/json");
    expect(payload).toMatchObject({ jsonrpc: "2.0", error: {
      code: -32600, message: expect.stringMatching(/Authorization.*x-api-key.*(match|conflict|disagree)/i),
    } });
    expect(text).not.toContain("bearer_secret");
    expect(text).not.toContain("alias_secret");
    expect(originFetch).not.toHaveBeenCalled();
  });

  it.each(["", "two words", "Bearer alias_secret"])("malformed x-api-key is refused without an origin call: %j", async key => {
    const { payload } = await rpc({ headers: { "x-api-key": key } });
    const { result, value } = readEnvelope(payload);
    expect(result.isError).toBe(true);
    expect(value).toMatchObject({ status: 401, body: { error: { code: "missing_api_key" } } });
    expect(originFetch).not.toHaveBeenCalled();
  });

  describe.each(["true", "false"])("DATA_SPLIT_ENABLED=%s", split => {
    it.each(dataCalls)("$name requires a key even with MCP_REQUIRE_API_KEY=false", async params => {
      for (const setting of [undefined, "true", "false"]) {
        const { response, payload } = await rpc({ params, env: {
          ...ENV, DATA_SPLIT_ENABLED: split, MCP_REQUIRE_API_KEY: setting, RANK: via,
        } });
        expect(response.status).toBe(200);
        const { result, value } = readEnvelope(payload);
        expect(result.isError).toBe(true);
        expect(value).toMatchObject({ status: 401, body: { error: { code: "missing_api_key" } } });
      }
      expect(via.fetch).not.toHaveBeenCalled();
      expect(originFetch).not.toHaveBeenCalled();
    });
  });

  it("never includes header keys in auth errors or logs", async () => {
    const logs = ["log", "info", "debug", "warn", "error", "trace"] as const;
    const spies = logs.map(method => vi.spyOn(console, method).mockImplementation(() => {}));
    for (const headers of [
      { authorization: "Bearer private_bearer_value", "x-api-key": "private_alias_value" },
      { "x-api-key": "private_alias_value invalid" },
      { "x-api-key": "private_alias_value" },
    ]) {
      originFetch.mockImplementation(async () => Response.json({ error: { code: "invalid_api_key" } }, { status: 401 }));
      const { text } = await rpc({ headers });
      expect(text).not.toContain("private_bearer_value");
      expect(text).not.toContain("private_alias_value");
    }
    const logged = JSON.stringify(spies.map(spy => spy.mock.calls));
    expect(logged).not.toContain("private_bearer_value");
    expect(logged).not.toContain("private_alias_value");
  });

  it("does not expose credentials from an origin transport exception", async () => {
    via.fetch.mockRejectedValue(new Error("Request failed with Authorization: Bearer transport_secret"));
    const errorLog = vi.spyOn(console, "error").mockImplementation(() => {});
    const { payload, text } = await rpc({
      headers: { authorization: "Bearer transport_secret" }, env: { ...ENV, RANK: via },
    });
    expect(readEnvelope(payload).value).toMatchObject({
      status: 0, body: { error: { code: "origin_unreachable" } },
    });
    expect(text).not.toContain("transport_secret");
    expect(JSON.stringify(errorLog.mock.calls)).not.toContain("transport_secret");
  });

  it("serves a public cacheable server card matching tools/list and initialize", async () => {
    const env = { ...ENV, MCP_REQUIRE_API_KEY: "true", RANK: via };
    const response = await workerFetch(new Request("http://localhost/.well-known/mcp/server-card.json"), env, context);
    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toContain("application/json");
    expect(response.headers.get("cache-control")).toBe("public, max-age=300");
    const card = z.object({
      serverInfo,
      authentication: z.object({ required: z.literal(true), schemes: z.array(z.string()) }),
      tools: z.array(tool),
    }).parse(await response.json());
    const listed = z.object({ result: z.object({ tools: z.array(tool) }) }).parse(
      (await rpc({ method: "tools/list", params: {}, env })).payload,
    );
    const initialized = z.object({ result: z.object({ serverInfo }) }).parse(
      (await rpc({ method: "initialize", params: initializeParams, env })).payload,
    );
    expect(card.tools).toEqual(listed.result.tools);
    expect(card.tools).toHaveLength(9);
    expect(card.authentication.schemes).toContain("bearer");
    expect(card.serverInfo).toEqual(initialized.result.serverInfo);
    expect(card.serverInfo).toEqual({ name: "modelspec", version: "model-403-test-commit" });
    expect(originFetch).not.toHaveBeenCalled();
    expect(via.fetch).not.toHaveBeenCalled();
  });
});
