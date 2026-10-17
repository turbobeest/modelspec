import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { z } from "zod";

import { workerFetch } from "../src/index";

const ENV: Env = {
  EXPORT_ORIGIN: "https://modelspec.dev",
  RANK_API_ORIGIN: "https://api.modelspec.dev",
  BUILD_COMMIT: "hardware-fit-test",
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
const request = {
  model: "lab/model", sku: "gpu-example", device_count: 2, memory: 80,
  runtime: "runtime-1", quantisation: "q4", batch: 4, context: 8192,
};

async function rpc(method: string, params: unknown, authorization?: string, env: Env = ENV) {
  const headers = new Headers({
    host: "localhost", "content-type": "application/json", accept: "application/json, text/event-stream",
  });
  if (authorization !== undefined) headers.set("authorization", authorization);
  const response = await workerFetch(new Request("http://localhost/mcp", {
    method: "POST", headers, body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }),
  }), env, context);
  expect(response.status).toBe(200);
  const text = await response.text();
  const payload = text.trim().startsWith("{") ? text : text.split("\n")
    .find(line => line.startsWith("data:"))?.slice(5);
  if (payload === undefined) throw new Error("MCP response has no JSON payload");
  const decoded: unknown = JSON.parse(payload);
  return decoded;
}

async function call(args: unknown, env: Env = ENV, authorization = "Bearer hardware_key") {
  return toolResult.parse(await rpc("tools/call", {
    name: "hardware_fit", arguments: args,
  }, authorization, env)).result;
}

function envelope(result: z.infer<typeof toolResult>["result"]) {
  const first = result.content[0];
  if (first === undefined) throw new Error("MCP response has no content");
  return envelopeSchema.parse(JSON.parse(first.text));
}

function jsonResponse(status: number, body: unknown) {
  return new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });
}

describe("hardware_fit MCP tool", () => {
  const originFetch = vi.fn();

  beforeEach(() => {
    originFetch.mockReset();
    vi.stubGlobal("fetch", originFetch);
  });
  afterEach(() => vi.unstubAllGlobals());

  it("lists an optional strict workload schema and distinguishes estimates from measured fit", async () => {
    const listing = z.object({ result: z.object({ tools: z.array(z.object({
      name: z.string(), description: z.string(), inputSchema: z.record(z.string(), z.unknown()),
    })) }) }).parse(await rpc("tools/list", {}));
    const tool = listing.result.tools.find(candidate => candidate.name === "hardware_fit");
    expect(tool).toBeDefined();
    if (tool === undefined) return;
    expect(tool.description).toContain("measured");
    expect(tool.description).toContain("estimated");
    expect(tool.description).toContain("undetermined");
    expect(tool.description).toContain("API key");
    expect(tool.description).toContain("per device");
    expect(tool.inputSchema.additionalProperties).toBe(false);
    expect(tool.inputSchema.required ?? []).toEqual([]);
    expect(Object.keys(z.record(z.string(), z.unknown()).parse(tool.inputSchema.properties))).toEqual([
      "model", "sku", "device_count", "memory", "runtime", "quantisation", "batch", "context",
    ]);
  });

  it.each([
    { status: "measured", measured_fit: true, measurement: { id: "run-1", source: "source-run" } },
    {
      status: "estimated", estimated_fit: "likely", margin_bytes: 1000,
      formula: "weights_bytes + kv_bytes_per_token * batch * context + runtime_headroom_bytes",
      inputs: { weights_bytes: 100, kv_bytes_per_token: 2, runtime_headroom_bytes: 30 },
      assumptions: ["Memory remains per device."],
    },
    { status: "undetermined", missing: [{ input: "quantisation", reason: "No sourced weights." }] },
  ])("preserves the complete $status response and forwards workload and bearer through the binding", async variant => {
    const body = {
      hardware_fit_version: "1.0", endpoint: "hardware-fit", snapshot: "snap_test", request,
      sources: [{ id: "source-run", url: "https://example.test/run" }], ...variant,
    };
    const via = { fetch: vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => jsonResponse(200, body)) };
    const result = await call(request, { ...ENV, RANK: via });
    expect(result.isError).toBe(false);
    expect(result.content).toHaveLength(1);
    expect(envelope(result)).toEqual({ origin: "https://api.modelspec.dev/v1/hardware-fit", status: 200, body });
    const [url, init] = via.fetch.mock.calls[0] ?? [];
    expect(url).toBe("https://api.modelspec.dev/v1/hardware-fit");
    expect(init?.method).toBe("POST");
    expect(JSON.parse(String(init?.body))).toEqual(request);
    expect(new Headers(init?.headers).get("authorization")).toBe("Bearer hardware_key");
    expect(originFetch).not.toHaveBeenCalled();
    if (variant.status === "estimated") {
      expect(envelope(result).body).not.toHaveProperty("fits");
      expect(envelope(result).body).not.toHaveProperty("measured_fit");
    }
  });

  it.each([
    {}, { model: "lab/model" }, { memory: null, runtime: null }, { ...request, sku: "unknown-sku" },
    { ...request, quantisation: "unpublished-quantisation" }, { ...request, context: 1_000_000_000 },
  ])("forwards incomplete and unsupported requests for an undetermined answer: %j", async args => {
    const body = {
      hardware_fit_version: "1.0", endpoint: "hardware-fit", snapshot: "snap_test", request: args,
      status: "undetermined", missing: [{ input: "source", reason: "Required input or source is absent." }],
      sources: [],
    };
    originFetch.mockResolvedValueOnce(jsonResponse(200, body));
    const result = await call(args);
    expect(result.isError).toBe(false);
    expect(envelope(result)).toEqual({ origin: "https://api.modelspec.dev/v1/hardware-fit", status: 200, body });
    const [, init] = originFetch.mock.calls[0] ?? [];
    expect(JSON.parse(String(init?.body))).toEqual(args);
  });

  it.each([undefined, "", "Bearer", "Basic hardware_key", "Bearer\thardware_key"])(
    "requires a bearer before fetching even when the optional access switch is false: %s", async authorization => {
      const via = { fetch: vi.fn(async () => jsonResponse(200, { status: "measured", measured_fit: true })) };
      const result = toolResult.parse(await rpc("tools/call", {
        name: "hardware_fit", arguments: request,
      }, authorization, { ...ENV, MCP_REQUIRE_API_KEY: "false", RANK: via })).result;
      expect(result.isError).toBe(true);
      expect(envelope(result)).toMatchObject({ status: 401, body: { error: { code: "missing_api_key" } } });
      expect(via.fetch).not.toHaveBeenCalled();
      expect(originFetch).not.toHaveBeenCalled();
    },
  );

  it.each([
    { ...request, device_count: 0 }, { ...request, device_count: 1.5 },
    { ...request, batch: -1 }, { ...request, context: 0 }, { ...request, context: "8192" },
    { ...request, memory: 0 }, { ...request, memory: 1_000_001 },
    { ...request, model: " " }, { ...request, runtime: "x".repeat(513) },
    { ...request, device_count: 1025 }, { ...request, batch: 1_000_001 },
    { ...request, context: 1_000_000_001 },
    { ...request, model: 123 }, { ...request, fits: true },
  ])("refuses invalid types, nonpositive values and unknown fields before fetching: %j", async args => {
    const result = await call(args);
    expect(result.isError).toBe(true);
    expect(result.content.map(block => block.text).join(" ")).not.toMatch(/not found/i);
    expect(originFetch).not.toHaveBeenCalled();
  });

  it.each([400, 401, 402, 403, 404, 500])("preserves an upstream %s refusal", async status => {
    const body = { error: { code: "upstream_refusal", message: "No assessment available" } };
    originFetch.mockResolvedValueOnce(jsonResponse(status, body));
    const result = await call(request);
    expect(result.isError).toBe(true);
    expect(envelope(result)).toEqual({ origin: "https://api.modelspec.dev/v1/hardware-fit", status, body });
  });
});
