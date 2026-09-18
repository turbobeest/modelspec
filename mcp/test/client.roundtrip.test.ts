import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { workerFetch } from "../src/index";
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

describe("MCP client round-trip", () => {
  const originFetch = vi.fn();

  beforeEach(() => {
    originFetch.mockReset();
    vi.stubGlobal("fetch", originFetch);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("lists tools and calls rank through the SDK client", async () => {
    const { Client, StreamableHTTPClientTransport } = await import(
      "@modelcontextprotocol/client"
    );

    originFetch.mockResolvedValue(
      new Response(JSON.stringify({ result: [{ model_id: "x" }] }), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );

    const transport = new StreamableHTTPClientTransport(
      new URL("http://localhost/mcp"),
      {
        fetch: (input: RequestInfo | URL, init?: RequestInit) => {
          const headers = new Headers(init?.headers);
          if (!headers.has("host")) {
            const url =
              typeof input === "string"
                ? input
                : input instanceof URL
                  ? input.href
                  : input.url;
            headers.set("host", new URL(url).host);
          }
          const request = new Request(input, { ...init, headers });
          return workerFetch(request, ENV, testCtx());
        },
      },
    );
    const client = new Client(
      { name: "vitest", version: "0" },
      { versionNegotiation: { mode: "auto" } },
    );
    await client.connect(transport);
    try {
      const listed = await client.listTools();
      expect(listed.tools.map((tool) => tool.name).sort()).toEqual(
        [...TOOL_NAMES].sort(),
      );
      const called = await client.callTool({
        name: "rank",
        arguments: { use_case: "coding", limit: 1 },
      });
      const text = (called.content as Array<{ type: string; text: string }>)[0]
        .text;
      const envelope = JSON.parse(text) as {
        origin: string;
        status: number;
        body: { result: Array<{ model_id: string }> };
      };
      expect(envelope.origin).toBe("https://api.modelspec.dev/v1/rank");
      expect(envelope.status).toBe(200);
      expect(envelope.body.result[0].model_id).toBe("x");
    } finally {
      await client.close();
    }
  });
});
