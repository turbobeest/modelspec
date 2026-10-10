import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { isCallToolResult } from "@modelcontextprotocol/server";

import { workerFetch } from "../src/index";
import { USER_AGENT } from "../src/origin";
import { AGENT_BYTES, defaultDecideRequest, fitDecideEnvelope, TOOL_NAMES } from "../src/server";
// Real Worker bodies from the public catalogue (python -m qa.decide_budget).
import budget from "./fixtures/decide-budget.json";

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
  headers: Record<string, string> = { authorization: "Bearer test_key" },
  env: Env = ENV,
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
    env,
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

  it("tools/list returns all seven tools with object input schemas", async () => {
    const listed = await rpc("tools/list", {});
    const result = listed.payload.result as {
      tools: Array<{ name: string; inputSchema: { type?: string } }>;
    };
    expect(result.tools.map((tool) => tool.name).sort()).toEqual(
      [...TOOL_NAMES].sort(),
    );
    expect(result.tools).toHaveLength(7);
    expect(result.tools).toMatchSnapshot();
    for (const tool of result.tools) {
      expect(tool.inputSchema).toBeTruthy();
      expect(tool.inputSchema.type ?? "object").toBe("object");
    }
  });

  it("decide describes compact defaults and stateless drill-down", async () => {
    const listed = await rpc("tools/list", {});
    const result = listed.payload.result as {
      tools: Array<{ name: string; description?: string }>;
    };
    const description = result.tools.find((tool) => tool.name === "decide")?.description;
    expect(description).toContain(
      "MCP decide returns a bounded answer of at most 16 KB, summary included.",
    );
    expect(description).toContain("explanation.fetch");
    expect(description).toContain('With explain unset or "none": explain=none, limit=10');
    expect(description).toContain("contributions and evidence");
    expect(description).toContain("omitted counts removed records");
    expect(description).toContain("including null");
    expect(description).toContain("https://modelspec.dev/agents.md");
    expect(description).not.toContain("explain=summary first");
  });

  it("initialize reports BUILD_COMMIT as serverInfo.version", async () => {
    const { payload } = await rpc("initialize", {
      protocolVersion: "2025-03-26",
      capabilities: {},
      clientInfo: { name: "vitest", version: "0" },
    });
    const result = payload.result as { serverInfo: { name: string; version: string }; instructions: string };
    expect(result.instructions).toContain("https://modelspec.dev/agents.md");
    expect(result.instructions).toContain("Call decide early");
    expect(result.instructions).toContain(
      "MCP decide returns a bounded answer of at most 16 KB, summary included.",
    );
    expect(result.instructions).not.toContain("explain=summary first");
    expect(result.instructions.length / 4).toBeLessThanOrEqual(1000);
    expect(result.serverInfo.name).toBe("modelspec");
    expect(result.serverInfo.version).toBe("test-commit-sha");
  });

  it("rank, policy_check, and decide go through the RANK binding", async () => {
    // Deployed, a same-zone fetch of api.modelspec.dev answered 522; the
    // binding is the path. The envelope still names the public URL.
    const bound = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => jsonResponse(200, { result: [] }));
    const env: Env = { ...ENV, RANK: { fetch: bound } as unknown as Fetcher };
    for (const name of ["rank", "policy_check", "decide"]) {
      const args =
        name === "rank"
          ? { use_case: "coding", limit: 1 }
          : name === "policy_check"
            ? { policy: { origin: { permitted_countries: ["US"] } }, limit: 1 }
            : { spec_version: 1, optimize: { min: "offering.cost_per_task" } };
      const { payload } = await rpc("tools/call", { name, arguments: args }, 1, { authorization: "Bearer test_key" }, env);
      expect(envelopeFromCall(payload).status).toBe(200);
    }
    expect(bound).toHaveBeenCalledTimes(3);
    for (const [, init] of bound.mock.calls) {
      expect(new Headers(init?.headers).get("authorization")).toBe("Bearer test_key");
    }
    expect(bound.mock.calls.map((c) => c[0])).toEqual([
      "https://api.modelspec.dev/v1/rank",
      "https://api.modelspec.dev/v1/policy-check",
      "https://api.modelspec.dev/v1/decide",
    ]);
    expect(originFetch).not.toHaveBeenCalled();
  });

  const decisionTools = [
    { name: "rank", arguments: { use_case: "coding" }, path: "/v1/rank" },
    { name: "policy_check", arguments: { policy: {} }, path: "/v1/policy-check" },
    { name: "decide", arguments: { spec_version: 1, optimize: { min: "offering.cost_per_task" } }, path: "/v1/decide" },
    { name: "vocab", arguments: {}, path: "/v1/vocabulary?section=starter&detail=compact" },
    { name: "model_info", arguments: { model_id: "lab/a" }, path: "/v1/vocabulary" },
  ];

  for (const tool of decisionTools) {
    it.each([undefined, "", "Bearer", "Bearer   ", "Basic test_key", "Bearer\ttest_key"])(
      `${tool.name} refuses absent or malformed credentials (%s) even if the API would answer free`,
      async (authorization) => {
        const bound = vi.fn(async () => jsonResponse(200, { results: [{ model: "free-answer" }] }));
        const env: Env = { ...ENV, DATA_SPLIT_ENABLED: "true", RANK: { fetch: bound } as unknown as Fetcher };
        const headers = authorization === undefined ? {} : { authorization };
        const { payload } = await rpc("tools/call", { name: tool.name, arguments: tool.arguments }, 1, headers, env);
        expect(envelopeFromCall(payload)).toEqual({
          origin: `https://api.modelspec.dev${tool.path}`,
          status: 401,
          body: {
            error: {
              code: "missing_api_key",
              message: "MCP data tools require an API key. Send Authorization: Bearer <key>. Get one at https://modelspec.dev/pricing/.",
              how_to_get_a_key: "https://modelspec.dev/pricing",
              docs: "https://modelspec.dev/docs/api",
            },
            result: [],
          },
        });
        const result = payload.result as { isError?: boolean; content: unknown[] };
        expect(result.isError).toBe(true);
        expect(result.content).toHaveLength(1);
        expect(bound).not.toHaveBeenCalled();
        expect(originFetch).not.toHaveBeenCalled();
      },
    );

    it.each([401, 402, 403])(`${tool.name} passes through the API's %s auth/payment refusal`, async (status) => {
      const body = { error: { code: "upstream_refusal", message: "No decision available" }, result: [] };
      const bound = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => jsonResponse(status, body));
      const env: Env = { ...ENV, DATA_SPLIT_ENABLED: "true", RANK: { fetch: bound } as unknown as Fetcher };
      const { payload } = await rpc("tools/call", { name: tool.name, arguments: tool.arguments }, 1, { authorization: "Bearer presented_key" }, env);
      expect(envelopeFromCall(payload)).toEqual({ origin: `https://api.modelspec.dev${tool.path}`, status, body });
      expect((payload.result as { isError?: boolean }).isError).toBe(true);
      const init = bound.mock.calls[0]?.[1] as RequestInit;
      expect(new Headers(init.headers).get("authorization")).toBe("Bearer presented_key");
    });
  }

  it.each(["true", "false"])("all static data tools require a key with split=%s", async (split) => {
    const bound = vi.fn();
    for (const tool of [
      { name: "vocab", arguments: {} },
      { name: "model_info", arguments: { model_id: "lab/a" } },
      { name: "list_use_cases", arguments: {} },
    ]) {
      const { payload } = await rpc("tools/call", tool, 1, {}, {
        ...ENV, DATA_SPLIT_ENABLED: split, RANK: { fetch: bound },
      });
      expect(envelopeFromCall(payload)).toMatchObject({
        status: 401,
        body: { error: {
          code: "missing_api_key",
          how_to_get_a_key: "https://modelspec.dev/pricing",
          message: expect.stringContaining("https://modelspec.dev/pricing"),
        }},
      });
    }
    expect(bound).not.toHaveBeenCalled();
    expect(originFetch).not.toHaveBeenCalled();
  });

  it.each([undefined, "true", "typo", "", "0"])("requires a key unless the MCP setting explicitly says false (%s)", async (setting) => {
    const { payload } = await rpc("tools/call", { name: "rank", arguments: { use_case: "coding" } }, 1, {}, { ...ENV, MCP_REQUIRE_API_KEY: setting });
    expect(envelopeFromCall(payload).status).toBe(401);
    expect(originFetch).not.toHaveBeenCalled();
  });

  it("permits anonymous calls only with the explicit MCP opt-out", async () => {
    originFetch.mockResolvedValueOnce(jsonResponse(200, { result: [] }));
    const { payload } = await rpc("tools/call", { name: "rank", arguments: { use_case: "coding" } }, 1, {}, { ...ENV, MCP_REQUIRE_API_KEY: "false" });
    expect(envelopeFromCall(payload).status).toBe(200);
    expect(originFetch).toHaveBeenCalledOnce();
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

  it("preserves the real speech coverage refusal, including covered classes and the keyless link", async () => {
    originFetch.mockResolvedValueOnce(jsonResponse(200, budget.speech));
    const { payload } = await rpc("tools/call", {
      name: "decide",
      arguments: budget.speech_request,
    });
    const envelope = envelopeFromCall(payload);
    expect(envelope.status).toBe(200);
    expect(envelope.body).toEqual(budget.speech);
    expect(budget.speech.coverage.kind).toBe("out_of_coverage");
    expect(budget.speech.coverage.requested_classes).toEqual(["transcriber"]);
    expect(budget.speech.coverage.classes.length).toBeGreaterThan(0);
    expect(budget.speech.coverage.url).toBe("https://modelspec.dev/api/coverage.json");
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

  it("feedback posts client mcp, forwards the caller address and never a key", async () => {
    const originBody = { status: "not_recorded", recorded: false };
    originFetch.mockResolvedValueOnce(jsonResponse(200, originBody));
    const { payload } = await rpc(
      "tools/call",
      {
        name: "feedback",
        arguments: { rating: "unreliable", decision_id: "dec_3f9a1c2b7d4e", note: "no EU region" },
      },
      1,
      { authorization: "Bearer live_secret", "CF-Connecting-IP": "203.0.113.7" },
    );
    const envelope = envelopeFromCall(payload);
    expect(envelope.origin).toBe("https://api.modelspec.dev/v1/feedback");
    expect(envelope.body).toEqual(originBody);
    const init = originFetch.mock.calls[0][1] as RequestInit;
    const headers = new Headers(init.headers);
    expect(headers.get("authorization")).toBeNull();
    expect(headers.get("x-modelspec-client-ip")).toBe("203.0.113.7");
    expect(JSON.parse(String(init.body))).toEqual({
      rating: "unreliable",
      decision_id: "dec_3f9a1c2b7d4e",
      note: "no EU region",
      client: "mcp",
    });
  });

  it("feedback refuses a rating outside the five before any request", async () => {
    const { payload } = await rpc("tools/call", {
      name: "feedback",
      arguments: { rating: "great" },
    });
    const result = payload.result as { isError?: boolean };
    expect(result.isError).toBe(true);
    expect(originFetch).not.toHaveBeenCalled();
  });

  it.each(["2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25"])(
    "decide returns the exact user paragraph with annotations on protocol %s", async (protocolVersion) => {
      originFetch.mockResolvedValueOnce(jsonResponse(200, budget.default));
      const { payload } = await rpc("tools/call", { name: "decide", arguments: budget.request }, 1,
        { authorization: "Bearer decide_key", "mcp-protocol-version": protocolVersion });
      const result = payload.result;
      if (!isCallToolResult(result)) throw new Error("expected an MCP tool result");
      expect(result.content).toEqual([
        { type: "text", text: JSON.stringify({ origin: "https://api.modelspec.dev/v1/decide", status: 200, body: budget.default }) },
        { type: "text", text: budget.default.summary_for_user, annotations: { audience: ["user"] } },
      ]);
    },
  );

  it("decide keeps the legacy status text on an earlier protocol without adding annotations", async () => {
    originFetch.mockResolvedValueOnce(jsonResponse(200, {
      status: "answered", answer: null, results: [], may_qualify: [],
      summary_for_user: "ModelSpec has no answer for this request, so it names no pick.",
    }));
    const { payload } = await rpc("tools/call", { name: "decide", arguments: budget.request }, 1,
      { authorization: "Bearer decide_key", "mcp-protocol-version": "2024-10-07" });
    const result = payload.result;
    if (!isCallToolResult(result)) throw new Error("expected an MCP tool result");
    expect(result.content[1]).toEqual({ type: "text", text: "status: answered; top models: none; may qualify: 0" });
  });

  it("decide counts both copies of the paragraph and keeps next_move through oversized origin trimming", async () => {
    const evidence = [{ items: [{ note: "é".repeat(20000) }] }];
    const originBody = {
      ...budget.default,
      results: [{ ...budget.default.results[0], evidence }, ...budget.default.results.slice(1)],
    };
    originFetch.mockResolvedValueOnce(jsonResponse(200, originBody));
    const { payload } = await rpc("tools/call", { name: "decide", arguments: budget.request }, 1,
      { authorization: "Bearer decide_key" });
    const result = payload.result;
    if (!isCallToolResult(result)) throw new Error("expected an MCP tool result");
    expect(result.content).toHaveLength(2);
    expect(result.content[1]).toEqual({ type: "text", text: budget.default.summary_for_user, annotations: { audience: ["user"] } });
    expect(result.content.reduce((total, block) => total + (block.type === "text" ? Buffer.byteLength(block.text, "utf8") : 0), 0)).toBeLessThanOrEqual(AGENT_BYTES);
    expect(envelopeFromCall(payload).body).toMatchObject({
      summary_for_user: budget.default.summary_for_user, next_move: budget.default.next_move,
      must_mention: budget.default.must_mention,
    });
    expect(envelopeFromCall(payload).body).toHaveProperty("explanation.omitted", {
      ...originBody.explanation.omitted,
      results: originBody.results.length - 1,
      may_qualify: originBody.explanation.omitted.may_qualify + originBody.may_qualify.length,
      "results.evidence": evidence.length,
      "results.estimates": originBody.results[0].estimates.length,
    });
  });

  it("decide never adds an annotated summary to an origin error", async () => {
    const body = { error: { code: "missing_api_key", message: "Send a key." }, summary_for_user: "Do not report this as an answer." };
    originFetch.mockResolvedValueOnce(jsonResponse(401, body));
    const { payload } = await rpc("tools/call", { name: "decide", arguments: budget.request }, 1,
      { authorization: "Bearer decide_key" });
    const result = payload.result;
    if (!isCallToolResult(result)) throw new Error("expected an MCP tool result");
    expect(result.isError).toBe(true);
    expect(result.content).toEqual([{ type: "text", text: JSON.stringify({ origin: "https://api.modelspec.dev/v1/decide", status: 401, body }) }]);
  });

  it("decide proxies the spec and summarizes the decision", async () => {
    const originBody = {
      status: "partial",
      results: [
        { offering: { model: "google/gemini-3-7-flash" } },
        { offering: { model: "google/gemini-3-7-flash" } },
        { offering: { model: "openai/gpt-6-sol" } },
      ],
      may_qualify: [{ model: "moonshot/kimi-k3" }],
    };
    originFetch.mockResolvedValueOnce(jsonResponse(200, originBody));
    const spec = {
      spec_version: 1,
      snapshot: "latest",
      exclude_benchmarks: ["swe_bench_pro"],
      where: ["model.context_window >= 200000"],
      optimize: { min: "offering.cost_per_task" },
    };
    const { payload } = await rpc(
      "tools/call",
      { name: "decide", arguments: spec },
      1,
      { authorization: "Bearer decide_key" },
    );
    const envelope = envelopeFromCall(payload);
    expect(envelope).toEqual({
      origin: "https://api.modelspec.dev/v1/decide",
      status: 200,
      body: originBody,
    });
    const result = payload.result as { content: Array<{ text: string }> };
    expect(result.content[1].text).toBe(
      "status: partial; top models: google/gemini-3-7-flash, openai/gpt-6-sol; may qualify: 1",
    );
    const [url, init] = originFetch.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("https://api.modelspec.dev/v1/decide");
    expect(init.method).toBe("POST");
    expect(JSON.parse(String(init.body))).toEqual(defaultDecideRequest(spec));
    expect(new Headers(init.headers).get("authorization")).toBe(
      "Bearer decide_key",
    );
  });

  it("decide keeps explicit controls and forwards stateless drill-down", async () => {
    const spec = { spec_version: 1, snapshot: "snap_fixed", optimize: { max: "software_engineering" },
      explain: "summary", limit: 1, fields: ["contributions"], evidence_for: "lab/example" };
    originFetch.mockResolvedValueOnce(jsonResponse(200, { reading: { do_not_claim: ["Keep the tie"] } }));
    const { payload } = await rpc("tools/call", { name: "decide", arguments: spec });
    expect(JSON.parse(String(originFetch.mock.calls[0][1].body))).toEqual(spec);
    expect(envelopeFromCall(payload).body).toEqual({ reading: { do_not_claim: ["Keep the tie"] } });
  });

  it("decide returns the exact annotated paragraph on a real drill-down", async () => {
    // results and may_qualify are empty on a drill-down by design.
    expect(budget.drill_down.results).toEqual([]);
    expect(budget.drill_down.may_qualify).toEqual([]);
    originFetch.mockResolvedValueOnce(jsonResponse(200, budget.drill_down));
    const { payload } = await rpc("tools/call", {
      name: "decide",
      arguments: { ...budget.request, evidence_for: budget.drill_down.model_evidence.model },
    });
    const result = payload.result;
    if (!isCallToolResult(result)) throw new Error("expected an MCP tool result");
    expect(result.content[1]).toEqual({ type: "text", text: budget.drill_down.summary_for_user, annotations: { audience: ["user"] } });
    expect(envelopeFromCall(payload).body).toMatchObject({
      model_evidence: { model: "anthropic/claude-opus-5-5", status: "ranked", rank: 1 },
    });
  });

  it("decide keeps eliminated drill-down status in JSON and annotates the unchanged paragraph", async () => {
    const body = {
      ...budget.drill_down,
      model_evidence: { ...budget.drill_down.model_evidence, model: "lab/b", status: "eliminated", rank: null },
    };
    originFetch.mockResolvedValueOnce(jsonResponse(200, body));
    const { payload } = await rpc("tools/call", {
      name: "decide", arguments: { ...budget.request, evidence_for: "lab/b" },
    });
    const result = payload.result;
    if (!isCallToolResult(result)) throw new Error("expected an MCP tool result");
    expect(result.content[1]).toEqual({ type: "text", text: body.summary_for_user, annotations: { audience: ["user"] } });
    expect(envelopeFromCall(payload).body).toMatchObject({ model_evidence: { model: "lab/b", status: "eliminated", rank: null } });
  });

  it.each([
    ["unset", {}, ["model_rank", "cost_per_task", "estimates", "p_best"]],
    ["none", { explain: "none" }, ["model_rank", "cost_per_task", "estimates", "p_best"]],
    ["summary", { explain: "summary" }, ["model_rank", "cost_per_task", "estimates", "p_best", "contributions", "evidence"]],
    ["full", { explain: "full" }, ["model_rank", "cost_per_task", "estimates", "p_best", "contributions", "evidence"]],
    ["full with fields", { explain: "full", fields: ["contributions"] }, ["contributions"]],
    ["full with null fields", { explain: "full", fields: null }, null],
  ])("decide keeps a bounded projection unless fields is explicit (%s)", async (_, controls, fields) => {
    originFetch.mockResolvedValueOnce(jsonResponse(200, { status: "ok", results: [] }));
    const spec = { spec_version: 1, optimize: { max: "software_engineering" }, ...controls };
    await rpc("tools/call", { name: "decide", arguments: spec });
    const sent = JSON.parse(String(originFetch.mock.calls[0][1].body));
    expect(sent.fields).toEqual(fields);
    expect(sent.limit).toBe(10);
    expect(sent.explain).toBe("explain" in controls ? controls.explain : "none");
  });

  it("decide replaces an over-budget body with a trimmed notice", async () => {
    const pad = "x".repeat(20_000);
    const huge = {
      contract_version: "2.14",
      status: "partial",
      answer: { kind: "tied", members: ["anthropic/claude-opus-5-5", "openai/gpt-6-astra"] },
      warnings: ["thin_evidence"],
      coverage: { kind: "covered" },
      results: [
        { rank: 1, offering: { model: "anthropic/claude-opus-5-5" }, evidence: [pad], warnings: [] },
        { rank: 2, offering: { model: "openai/gpt-6-astra" }, evidence: [pad], warnings: [] },
      ],
      may_qualify: [{ model: "lab/z" }, { model: "lab/y" }],
    };
    originFetch.mockResolvedValueOnce(jsonResponse(200, huge));
    const { payload } = await rpc("tools/call", {
      name: "decide",
      arguments: {
        spec_version: 1,
        optimize: { max: "software_engineering" },
        explain: "full",
        fields: null,
      },
    });
    const result = payload.result as { content: Array<{ text: string }> };
    const textBytes = result.content.reduce((sum, block) => sum + Buffer.byteLength(block.text, "utf8"), 0);
    expect(textBytes).toBeLessThanOrEqual(16_384);
    const envelope = JSON.parse(result.content[0].text) as {
      body: {
        answer: { members: string[] };
        status: string;
        warnings: string[];
        coverage: { kind: string };
        explanation: { omitted: Record<string, number>; fetch: string };
        results: Array<{ offering: { model: string } }>;
      };
    };
    expect(envelope.body.status).toBe("partial");
    expect(envelope.body.answer.members).toEqual(huge.answer.members);
    expect(envelope.body.warnings).toEqual(huge.warnings);
    expect(envelope.body.coverage).toEqual(huge.coverage);
    expect(envelope.body.results).toHaveLength(1);
    expect(envelope.body.results[0].offering.model).toBe("anthropic/claude-opus-5-5");
    expect(envelope.body.explanation.omitted.results).toBeGreaterThan(0);
    expect(envelope.body.explanation.fetch).toContain("evidence_for: anthropic/claude-opus-5-5");
    expect(envelope.body.explanation.fetch).toContain("POST /v1/decide without fields");
    expect(result.content[1].text).toContain("anthropic/claude-opus-5-5");
    expect(result.content[1].text).not.toContain("top models: none");
  });

  it("decide passes member_evidence through when the body is inside the budget", async () => {
    const body = {
      representation: "bounded",
      bounded_version: "1.1",
      projects_contract: "2.14",
      status: "answered",
      answer: { kind: "tied", members: ["lab/a", "lab/b"] },
      warnings: [],
      results: [{ rank: 1, model: "lab/a", offering: { model: "lab/a" }, warnings: [], evidence: [] }],
      may_qualify: [],
      member_evidence: [
        {
          model: "lab/a",
          evidence: [{
            domain: "software_engineering",
            items: [{ record_id: "lab/a#swe_bench_pro#70", benchmark: "swe_bench_pro", value: 70 }],
          }],
          omitted_items: 1,
        },
        { model: "lab/b", evidence: [], omitted_items: 0 },
      ],
      explanation: {
        not_applied: [],
        omitted: {},
        note: "Projected rows are incomplete; omissions are not eliminations or absent evidence.",
      },
    };
    originFetch.mockResolvedValueOnce(jsonResponse(200, body));
    const { payload } = await rpc("tools/call", {
      name: "decide",
      arguments: { spec_version: 1, optimize: { max: "software_engineering" }, explain: "summary" },
    });
    const result = payload.result as { content: Array<{ text: string }> };
    const envelope = JSON.parse(result.content[0].text) as { body: typeof body };
    expect(envelope.body.member_evidence).toEqual(body.member_evidence);
    expect(envelope.body.bounded_version).toBe("1.1");
    expect(result.content[1].text).toBe("status: answered; top models: lab/a; may qualify: 0");
  });

  it("decide drops member_evidence before it shortens answer.members", () => {
    const members = Array.from({ length: 12 }, (_, index) => `lab/model-${index}`);
    const pad = "e".repeat(1_500);
    const memberEvidence = members.map((model) => ({
      model,
      evidence: [{
        domain: "software_engineering",
        items: [{ record_id: `${model}#swe`, benchmark: "swe_bench_pro", value: 70, note: pad }],
      }],
      omitted_items: 0,
    }));
    const fitted = fitDecideEnvelope({
      origin: "https://api.modelspec.dev/v1/decide",
      status: 200,
      body: {
        representation: "bounded",
        bounded_version: "1.1",
        projects_contract: "2.14",
        status: "answered",
        answer: { kind: "tied", members },
        warnings: [],
        results: [{ rank: 1, model: members[0], offering: { model: members[0] }, warnings: [] }],
        may_qualify: [],
        member_evidence: memberEvidence,
        explanation: {
          not_applied: [],
          omitted: {},
          note: "Projected rows are incomplete; omissions are not eliminations or absent evidence.",
        },
      },
    });
    const packed = JSON.stringify(fitted);
    expect(Buffer.byteLength(packed, "utf8")).toBeLessThanOrEqual(AGENT_BYTES);
    expect(packed).not.toContain(pad);
    const parsed: unknown = JSON.parse(packed);
    if (typeof parsed !== "object" || parsed === null || !("body" in parsed)) {
      throw new Error("fitted envelope has no body");
    }
    const body: unknown = parsed.body;
    if (typeof body !== "object" || body === null) throw new Error("fitted body is empty");
    expect("member_evidence" in body).toBe(false);
    expect("answer" in body && body.answer).toMatchObject({ kind: "tied", members });
    expect("explanation" in body && body.explanation).toMatchObject({
      omitted: { member_evidence: members.length },
    });
  });

  it("decide keeps a drill-down summary when the evidence body is over budget", async () => {
    const pad = "x".repeat(20_000);
    const huge = {
      status: "partial",
      answer: { kind: "separated", members: ["lab/a"], leader: "lab/a" },
      results: [],
      may_qualify: [],
      model_evidence: {
        model: "lab/a",
        status: "ranked",
        rank: 1,
        offering: { model: "lab/a" },
        evidence: [{ items: [{ source: pad }] }],
        contributions: [{ dimension: "software_engineering" }],
      },
    };
    originFetch.mockResolvedValueOnce(jsonResponse(200, huge));
    const { payload } = await rpc("tools/call", {
      name: "decide",
      arguments: { spec_version: 1, optimize: { max: "software_engineering" }, evidence_for: "lab/a" },
    });
    const result = payload.result as { content: Array<{ text: string }> };
    const textBytes = result.content.reduce((sum, block) => sum + Buffer.byteLength(block.text, "utf8"), 0);
    expect(textBytes).toBeLessThanOrEqual(16_384);
    expect(result.content[1].text).toContain("evidence for: lab/a (ranked, rank 1)");
    expect(result.content[1].text).not.toContain("top models: none");
    const envelope = JSON.parse(result.content[0].text) as {
      body: { explanation: { omitted: Record<string, number>; fetch: string } };
    };
    expect(Object.keys(envelope.body.explanation.omitted).length).toBeGreaterThan(0);
    expect(envelope.body.explanation.fetch).toContain("evidence_for: lab/a");
  });

  it("decide strips a copied reading instead of returning the raw body", async () => {
    const pad = "y".repeat(30_000);
    const huge = {
      status: "partial",
      answer: { kind: "separated", members: ["lab/a"], leader: "lab/a" },
      warnings: ["thin_evidence"],
      coverage: { kind: "covered" },
      reading: { do_not_claim: [pad] },
      results: [{ rank: 1, offering: { model: "lab/a", provider: "lab" }, warnings: [], evidence: [pad] }],
      may_qualify: [{ model: "lab/z" }],
    };
    originFetch.mockResolvedValueOnce(jsonResponse(200, huge));
    const { payload } = await rpc("tools/call", {
      name: "decide",
      arguments: { spec_version: 1, optimize: { max: "software_engineering" }, fields: null },
    });
    const result = payload.result as { content: Array<{ text: string }> };
    const text = result.content.map((block) => block.text).join("\n");
    const textBytes = result.content.reduce((sum, block) => sum + Buffer.byteLength(block.text, "utf8"), 0);
    expect(textBytes).toBeLessThanOrEqual(16_384);
    expect(text).not.toContain(pad);
    const envelope = JSON.parse(result.content[0].text) as {
      body: { status: string; answer: { members: string[] }; explanation: { fetch: string; omitted: Record<string, number> } };
    };
    expect(envelope.body.status).toBe("partial");
    expect(envelope.body.answer.members).toEqual(["lab/a"]);
    expect(envelope.body.explanation.fetch).toContain("POST /v1/decide without fields");
    expect(envelope.body.explanation.omitted.reading).toBeGreaterThan(0);
  });

  it("decide replaces an over-budget error without its raw text", () => {
    const pad = "SECRET".repeat(8_000);
    const fitted = fitDecideEnvelope({
      origin: "https://api.modelspec.dev/v1/decide",
      status: 400,
      body: { error: { code: pad, message: pad } },
    });
    const packed = JSON.stringify(fitted);
    expect(Buffer.byteLength(packed, "utf8")).toBeLessThanOrEqual(AGENT_BYTES);
    expect(packed).not.toContain(pad);
    expect(JSON.stringify(fitted.body)).toContain("POST /v1/decide without fields");
  });

  it("decide returns an upstream invalid_spec error with its code and message", async () => {
    const originBody = {
      error: {
        code: "invalid_spec", message: "where[0] names an unknown facet",
        recovery: [{
          path: "where[0]", accepted_shape: "a valid facet ID",
          example: { spec_version: 1, optimize: { max: "model.context_window" } },
          guidance: "Read vocab section=starter", nearest_facet_ids: ["model.context_window"],
        }],
        recovery_omitted: 0,
      },
    };
    originFetch.mockResolvedValueOnce(jsonResponse(400, originBody));
    const { payload } = await rpc("tools/call", {
      name: "decide",
      arguments: { spec_version: 1, optimize: { min: "not_a_facet" } },
    });
    const envelope = envelopeFromCall(payload);
    expect(envelope.status).toBe(400);
    expect(envelope.body).toEqual(originBody);
    expect((payload.result as { isError?: boolean }).isError).toBe(true);
  });

  it("decide returns an out-of-vocabulary value issue with its allowed values (MODEL-318)", async () => {
    const originBody = {
      error: {
        code: "invalid_spec", message: "the request body is not a valid decision spec",
        issues: [{
          path: "where[0]", condition: "model.weights_openness = proprietary",
          field: "model.weights_openness",
          reason: "'proprietary' is not a registered value of model.weights_openness",
          value: "proprietary", value_type: "enum",
          allowed_values: ["closed_weights", "open_weights"],
          next: "https://api.modelspec.dev/v1/vocabulary?section=facets&id=model.weights_openness",
        }],
      },
    };
    originFetch.mockResolvedValueOnce(jsonResponse(400, originBody));
    const { payload } = await rpc("tools/call", {
      name: "decide",
      arguments: {
        spec_version: 1, where: ["model.weights_openness = proprietary"],
        optimize: { max: "model.context_window" },
      },
    });
    const envelope = envelopeFromCall(payload);
    expect(envelope.status).toBe(400);
    expect(envelope.body).toEqual(originBody);
    expect((payload.result as { isError?: boolean }).isError).toBe(true);
  });

  it.each([
    { where: {} },
    { capabilities: [] },
    { optimize: "lowest price" },
  ])("decide forwards malformed input for Worker recovery: %j", async (invalid) => {
    const arguments_ = { spec_version: 1, optimize: { max: "model.context_window" }, ...invalid };
    const originBody = {
      contract_version: "2.12", endpoint: "decide", snapshot: "snap_test",
      error: {
        code: "invalid_spec", message: "the request body is not a valid decision spec",
        issues: [{ path: Object.keys(invalid)[0], reason: "wrong shape" }],
        recovery: [{
          path: Object.keys(invalid)[0], accepted_shape: "structured Spec field",
          example: { spec_version: 1, optimize: { max: "model.context_window" } },
          guidance: "Read vocab section=starter", nearest_facet_ids: [],
        }],
        recovery_omitted: 0,
      },
    };
    originFetch.mockResolvedValueOnce(jsonResponse(400, originBody));
    const { payload } = await rpc("tools/call", { name: "decide", arguments: arguments_ });
    expect(envelopeFromCall(payload).body).toEqual(originBody);
    expect((payload.result as { isError?: boolean }).isError).toBe(true);
    const [url, init] = originFetch.mock.calls[0];
    expect(url).toBe("https://api.modelspec.dev/v1/decide");
    expect(JSON.parse(String(init.body))).toEqual(defaultDecideRequest(arguments_));
  });

  it("vocab defaults to starter facets from template specs", async () => {
    const vocabulary = {
      facets: [{ id: "model.context_window" }],
      task_types: ["new_feature"],
      templates: [{ spec: { where: ["model.context_window >= 32000"] } }],
    };
    originFetch.mockResolvedValueOnce(jsonResponse(200, vocabulary));
    const { payload } = await rpc("tools/call", {
      name: "vocab",
      arguments: {},
    });
    const envelope = envelopeFromCall(payload);
    expect(envelope.origin).toBe(
      "https://modelspec.dev/api/decision/vocabulary.json",
    );
    expect(envelope.body).toEqual({ starter: vocabulary.facets,
      spec: { spec_version: 1, optimize: { min: "offering.cost_per_task" } },
      next: "next: call decide with this; refine from reading" });
  });

  it("vocab returns only the requested section", async () => {
    const facets = [{ id: "model.context_window" }];
    originFetch.mockResolvedValueOnce(
      jsonResponse(200, { facets, task_types: ["new_feature"] }),
    );
    const { payload } = await rpc("tools/call", {
      name: "vocab",
      arguments: { section: "facets" },
    });
    expect(envelopeFromCall(payload).body).toEqual({ facets,
      next: "next: call decide using these ids; refine from reading" });
  });
});

describe("private display vocabulary", () => {
  it("vocab and model_info use the trimmed Worker response without sentinel facts", async () => {
    const vocabulary = { facets: [], domains: [], templates: [], models: { "lab/model247-private-sentinel-8675309": { display_name: "model247-private-sentinel-8675309" } }, estate: { plans: [{ id: "plan", name: "Plan" }] } };
    const forbidden = ["8675.309123", "50.1234567"];
    // This active model must exist in the response: a missing-model refusal
    // would make the assertions pass without exercising model_info.
    const untrimmed = { ...vocabulary, models: { "lab/model247-private-sentinel-8675309": {
      display_name: "model247-private-sentinel-8675309", price: 8675.309123, score: 50.1234567,
    } } };
    for (const value of forbidden) expect(JSON.stringify(untrimmed)).toContain(value);
    const via = { fetch: vi.fn().mockImplementation(async () => jsonResponse(200, vocabulary)) };
    const env = { ...ENV, DATA_SPLIT_ENABLED: "true", RANK: via };
    for (const [name, args] of [["vocab", { section: "models", detail: "full" }], ["model_info", { model_id: "lab/model247-private-sentinel-8675309" }]] as const) {
      via.fetch.mockImplementationOnce(async () => jsonResponse(200, untrimmed));
      const control = await rpc("tools/call", { name, arguments: args }, 1, { authorization: "Bearer test_key", "CF-Connecting-IP": "203.0.113.9" }, env);
      for (const value of forbidden) expect(JSON.stringify(envelopeFromCall(control.payload).body)).toContain(value);
      const { payload } = await rpc("tools/call", { name, arguments: args }, 1, { authorization: "Bearer test_key", "CF-Connecting-IP": "203.0.113.9" }, env);
      const envelope = envelopeFromCall(payload);
      expect(envelope.status).toBe(200);
      expect(envelope.origin).toBe(name === "vocab" ? "https://api.modelspec.dev/v1/vocabulary?section=models&detail=full" : "https://api.modelspec.dev/v1/vocabulary");
      expect(JSON.stringify(envelope.body)).toContain("model247-private-sentinel-8675309");
      for (const value of forbidden) expect(JSON.stringify(envelope.body)).not.toContain(value);
    }
    expect(via.fetch).toHaveBeenCalledTimes(4);
    for (const [, init] of via.fetch.mock.calls) {
      expect(new Headers(init?.headers).get("authorization")).toBe("Bearer test_key");
    }
  });
});

describe("compact HTTP vocabulary requests", () => {
  it("returns identical scoped lookup envelopes from the Worker and the export", async () => {
    const vocabulary = { domains: [{ id: "chat_preference", name: "Chat and preference" }] };
    for (const [search, selected] of [
      ["chat", { domains: vocabulary.domains,
        matches: [{ section: "domains", id: "chat_preference", label: "Chat and preference", matched: "id" }],
        total: 1, searched: ["domains"], next: "next: call decide using these ids; refine from reading" }],
      ["zzzqqq", { domains: [], matches: [], total: 0, searched: ["domains"], suggestions: [],
        message: 'No vocabulary entry matches "zzzqqq" in the id, label, definition or values of domains; closest ids: none.',
        next: "next: retry vocab with one of the suggestions" }],
    ] satisfies [string, object][]) {
      const body = { facets: [], templates: [], models: {}, estate: {}, ...selected };
      const via = { fetch: vi.fn().mockResolvedValue(jsonResponse(200, body)) };
      const split = await rpc("tools/call", { name: "vocab", arguments: { section: "domains", search } }, 1,
        { authorization: "Bearer test_key" }, { ...ENV, DATA_SPLIT_ENABLED: "true", RANK: via });
      vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(200, vocabulary)));
      try {
        const exported = await rpc("tools/call", { name: "vocab", arguments: { section: "domains", search } });
        expect(envelopeFromCall(split.payload).body).toEqual(body);
        expect(envelopeFromCall(exported.payload).body).toEqual(body);
      } finally {
        vi.unstubAllGlobals();
      }
    }
  });

  it("passes cross-section rows and lookup metadata through from the Worker", async () => {
    const hits = {
      starter: [], facets: [{ id: "offering.price.input", label: "Input price" }],
      domains: [{ id: "price_domain", name: "Price" }], templates: [], models: {}, estate: {},
      providers: { price_provider: "Price provider" },
      matches: [{ section: "facets", id: "offering.price.input", label: "Input price", matched: "id" }],
      total: 3, searched: ["facets", "domains", "providers"],
      next: "next: call decide using these ids; refine from reading",
      spec: { spec_version: 1, optimize: { min: "offering.cost_per_task" } },
    };
    const miss = { starter: [], facets: [], domains: [], templates: [], models: {}, estate: {},
      matches: [], total: 0, searched: ["facets", "domains", "providers"],
      suggestions: [{ section: "facets", id: "offering.price.input" }], message: "No entry matches pirce.",
      next: "next: retry vocab with one of the suggestions", spec: hits.spec,
    };
    for (const [search, body] of [["price", hits], ["pirce", miss]] satisfies [string, object][]) {
      const via = { fetch: vi.fn().mockResolvedValue(jsonResponse(200, body)) };
      const { payload } = await rpc("tools/call", { name: "vocab", arguments: { search } }, 1,
        { authorization: "Bearer test_key" }, { ...ENV, DATA_SPLIT_ENABLED: "true", RANK: via });
      expect(envelopeFromCall(payload).body).toMatchObject(body);
      expect(payload.result).toMatchObject({ content: expect.arrayContaining([{ type: "text", text: body.next }]) });
    }
  });

  it("forwards the lookup options through the service binding and selects its section", async () => {
    const rows = [{ id: "model.context_window", operators: [">="] }];
    const via = { fetch: vi.fn().mockResolvedValue(jsonResponse(200, { facets: rows })) };
    const { payload } = await rpc("tools/call", {
      name: "vocab",
      arguments: { section: "facets", search: "CONTEXT", id: "model.context_window", ids: ["missing"], offset: 1, limit: 2 },
    }, 1, { authorization: "Bearer test_key", "CF-Connecting-IP": "203.0.113.9" }, { ...ENV, DATA_SPLIT_ENABLED: "true", RANK: via });
    const envelope = envelopeFromCall(payload);
    expect(envelope.body).toEqual({ facets: rows,
      next: "next: call decide using these ids; refine from reading" });
    const url = new URL(envelope.origin);
    expect(Object.fromEntries(url.searchParams)).toEqual({ section: "facets", detail: "compact", search: "CONTEXT", id: "model.context_window", ids: "missing", offset: "1", limit: "2" });
    const [, init] = via.fetch.mock.calls[0];
    expect(new Headers(init.headers).get("authorization")).toBe("Bearer test_key");
    expect(new Headers(init.headers).get("CF-Connecting-IP")).toBe("203.0.113.9");
  });

  it("defaults the HTTP lookup to starter and compact", async () => {
    const via = { fetch: vi.fn().mockResolvedValue(jsonResponse(200, { starter: [] })) };
    const { payload } = await rpc("tools/call", { name: "vocab", arguments: {} }, 1, { authorization: "Bearer test_key" }, { ...ENV, DATA_SPLIT_ENABLED: "true", RANK: via });
    expect(envelopeFromCall(payload).origin).toBe("https://api.modelspec.dev/v1/vocabulary?section=starter&detail=compact");
    expect(envelopeFromCall(payload).body).toEqual({ starter: [],
      spec: { spec_version: 1, optimize: { min: "offering.cost_per_task" } },
      next: "next: call decide with this; refine from reading" });
  });
});

describe("vocabulary rollout", () => {
  it("compacts a legacy Worker response that ignores the query parameters", async () => {
    const via = { fetch: vi.fn().mockResolvedValue(jsonResponse(200, {
      vocabulary_version: 1,
      facets: [{ id: "model.context_window", label: "Context", definition: "Token window. More details.", value_type: "number", operators: [">="], has_data: true }],
      templates: [{ spec: { where: ["model.context_window >= 32000"] } }],
    })) };
    const { payload } = await rpc("tools/call", { name: "vocab", arguments: {} }, 1, { authorization: "Bearer test_key" }, { ...ENV, DATA_SPLIT_ENABLED: "true", RANK: via });
    expect(envelopeFromCall(payload).body).toEqual({ starter: [{ id: "model.context_window", label: "Context", definition: "Token window.", value_type: "number" }],
      spec: { spec_version: 1, optimize: { min: "offering.cost_per_task" } },
      next: "next: call decide with this; refine from reading" });
  });
});
