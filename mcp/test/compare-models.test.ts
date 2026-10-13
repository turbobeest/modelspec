import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { z } from "zod";

import { workerFetch } from "../src/index";
import { AGENT_BYTES } from "../src/server";

const ENV: Env = {
  EXPORT_ORIGIN: "https://modelspec.dev",
  RANK_API_ORIGIN: "https://api.modelspec.dev",
  BUILD_COMMIT: "compare-models-test",
};
const context: ExecutionContext = {
  waitUntil(promise) { void promise; },
  passThroughOnException() {},
  props: {},
};
const toolResult = z.object({
  result: z.object({
    content: z.array(z.object({ type: z.literal("text"), text: z.string() })).min(1),
    isError: z.boolean().optional(),
  }),
});
const envelopeSchema = z.object({ origin: z.string(), status: z.number(), body: z.unknown() });

async function rpc(method: string, params: unknown, authorization?: string, env: Env = ENV) {
  const headers = new Headers({
    host: "localhost",
    "content-type": "application/json",
    accept: "application/json, text/event-stream",
  });
  if (authorization !== undefined) headers.set("authorization", authorization);
  const response = await workerFetch(new Request("http://localhost/mcp", {
    method: "POST", headers,
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }),
  }), env, context);
  expect(response.status).toBe(200);
  const text = await response.text();
  const payload = text.trim().startsWith("{") ? text : text.split("\n")
    .find(line => line.startsWith("data:"))?.slice(5);
  if (payload === undefined) throw new Error("MCP response has no JSON payload");
  const decoded: unknown = JSON.parse(payload);
  return decoded;
}

async function call(args: unknown, authorization = "Bearer compare_key", env: Env = ENV) {
  const payload = await rpc("tools/call", { name: "compare_models", arguments: args }, authorization, env);
  return toolResult.parse(payload).result;
}

function envelope(result: z.infer<typeof toolResult>["result"]) {
  const first = result.content[0];
  if (first === undefined) throw new Error("MCP response has no content");
  return envelopeSchema.parse(JSON.parse(first.text));
}

function jsonResponse(status: number, body: unknown) {
  return new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });
}

describe("compare_models MCP tool", () => {
  const originFetch = vi.fn();

  beforeEach(() => {
    originFetch.mockReset();
    vi.stubGlobal("fetch", originFetch);
  });
  afterEach(() => vi.unstubAllGlobals());

  it("lists a strict bounded model list and describes caller order without ranking", async () => {
    const listing = z.object({ result: z.object({ tools: z.array(z.object({
      name: z.string(), description: z.string(), inputSchema: z.record(z.string(), z.unknown()),
    })) }) }).parse(await rpc("tools/list", {}));
    const tool = listing.result.tools.find(candidate => candidate.name === "compare_models");
    expect(tool).toBeDefined();
    if (tool === undefined) return;
    expect(tool.description).toContain("caller order");
    expect(tool.description).toContain("does not rank");
    expect(tool.description).toContain("API key");
    expect(tool.inputSchema.additionalProperties).toBe(false);
    expect(tool.inputSchema.required).toEqual(["models"]);
    const properties = z.object({ models: z.object({ minItems: z.number(), maxItems: z.number() }) })
      .parse(tool.inputSchema.properties);
    expect(properties.models).toEqual({ minItems: 2, maxItems: 4 });
  });

  it.each([
    ["lab/b", "lab/a"],
    ["lab/d", "lab/b", "lab/c", "lab/a"],
  ])("forwards named models in caller order and preserves snapshot facts: %j", async (...models) => {
    const body = {
      comparison_version: "1.0", endpoint: "compare-models", snapshot: "snap_test",
      models: models.map(model => ({
        model, facts: [{ facet: "model.context_window", value: null }], offerings: [], evidence: [],
      })),
      sources: [], omitted: {},
    };
    const via = { fetch: vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => jsonResponse(200, body)) };
    const result = await call({ models }, "Bearer compare_key", { ...ENV, RANK: via });
    expect(result.isError).toBe(false);
    expect(result.content).toHaveLength(1);
    expect(envelope(result)).toEqual({ origin: "https://api.modelspec.dev/v1/compare-models", status: 200, body });
    expect(via.fetch).toHaveBeenCalledOnce();
    const [url, init] = via.fetch.mock.calls[0] ?? [];
    expect(url).toBe("https://api.modelspec.dev/v1/compare-models");
    expect(init?.method).toBe("POST");
    expect(JSON.parse(String(init?.body))).toEqual({ models });
    expect(new Headers(init?.headers).get("authorization")).toBe("Bearer compare_key");
    expect(originFetch).not.toHaveBeenCalled();
  });

  it.each([undefined, "", "Bearer", "Basic compare_key", "Bearer\tcompare_key"])(
    "refuses absent or malformed credentials before fetching: %s", async authorization => {
      const via = { fetch: vi.fn(async () => jsonResponse(200, { models: [] })) };
      const result = toolResult.parse(await rpc("tools/call", {
        name: "compare_models", arguments: { models: ["lab/a", "lab/b"] },
      }, authorization, { ...ENV, RANK: via })).result;
      expect(result.isError).toBe(true);
      expect(envelope(result)).toMatchObject({ status: 401, body: { error: { code: "missing_api_key" } } });
      expect(via.fetch).not.toHaveBeenCalled();
      expect(originFetch).not.toHaveBeenCalled();
    },
  );

  it.each([
    {}, { models: [] }, { models: ["lab/a"] },
    { models: ["lab/a", "lab/b", "lab/c", "lab/d", "lab/e"] },
    { models: ["lab/a", "lab/a"] }, { models: ["lab/a", "LAB/b"] },
    { models: ["lab/a", "lab"] }, { models: ["lab/a", "lab/b/c"] },
    { models: ["lab/a", "lab/b?secret=key"] },
    { models: ["lab/a", `lab/${"b".repeat(125)}`] },
    { models: ["lab/a", "lab/b"], spec: {} },
  ])("refuses invalid input before fetching: %j", async args => {
    const result = await call(args);
    expect(result.isError).toBe(true);
    expect(result.content.map(block => block.text).join(" ")).not.toMatch(/not found/i);
    expect(originFetch).not.toHaveBeenCalled();
  });

  it.each([400, 401, 402, 403, 404])("preserves an upstream %s refusal", async status => {
    const body = { error: { code: "upstream_refusal", message: "No comparison available" } };
    originFetch.mockResolvedValueOnce(jsonResponse(status, body));
    const result = await call({ models: ["lab/a", "lab/b"] });
    expect(result.isError).toBe(true);
    expect(envelope(result)).toEqual({ origin: "https://api.modelspec.dev/v1/compare-models", status, body });
  });

  it.each([
    { models: ["lab/a", "lab/b"], ["private".repeat(4_000)]: true },
    { models: Array.from({ length: 2_000 }, () => "invalid-model") },
  ])("bounds validation errors for oversized invalid input", async args => {
    const result = await call(args);
    expect(result.isError).toBe(true);
    const text = result.content.map(block => block.text).join("\n");
    expect(Buffer.byteLength(text, "utf8")).toBeLessThanOrEqual(AGENT_BYTES);
    expect(originFetch).not.toHaveBeenCalled();
  });

  it.each(["success", "error", "network", "origin"])(
    "refuses an oversized %s with a compact error within the entire text budget", async kind => {
      const pad = "private😀".repeat(4_000);
      if (kind === "network") originFetch.mockRejectedValueOnce(new Error(pad));
      else originFetch.mockResolvedValueOnce(jsonResponse(kind === "error" ? 400 : 200,
        kind === "error" ? { error: { code: pad, message: pad } } : { models: [], sources: [pad] }));
      const env = kind === "origin" ? { ...ENV, RANK_API_ORIGIN: `https://example.test/${pad}` } : ENV;
      const result = await call({ models: ["lab/a", "lab/b"] }, "Bearer compare_key", env);
      expect(result.isError).toBe(true);
      const text = result.content.map(block => block.text).join("\n");
      expect(Buffer.byteLength(text, "utf8")).toBeLessThanOrEqual(AGENT_BYTES);
      expect(text).toContain("response_too_large");
      expect(text).toContain("No comparison data was returned");
      expect(text).not.toContain(pad);
      expect(text).not.toContain('"representation":"bounded"');
      expect(text).not.toContain("decide");
    },
  );
});
