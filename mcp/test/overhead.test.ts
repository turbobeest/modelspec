import { writeFileSync } from "node:fs";
import { expect, it } from "vitest";
import { z } from "zod";
import { mcpHandler } from "../src/server";
import agentCopy from "../src/agent-copy.json";
import decisionContract from "../../docs/decision-contract.schema.json";

const listing = z.object({
  result: z.object({
    tools: z.array(z.object({
      name: z.string(), description: z.string(),
      inputSchema: z.record(z.string(), z.unknown()),
    }).passthrough()),
  }),
});

it("bounds descriptions and emits only DecideRequest-reachable definitions", async () => {
  const env: Env = {
    EXPORT_ORIGIN: "https://modelspec.dev",
    RANK_API_ORIGIN: "https://api.modelspec.dev", BUILD_COMMIT: "size-test",
  };
  const ctx: ExecutionContext = {
    waitUntil(promise) { void promise; }, passThroughOnException() {}, props: {},
  };
  const response = await mcpHandler(env)(new Request("http://localhost/mcp", {
    method: "POST", headers: {
      host: "localhost", "content-type": "application/json", accept: "application/json, text/event-stream",
    }, body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/list", params: {} }),
  }), env, ctx);
  const text = await response.text();
  const payload = text.trim().startsWith("{") ? text : text.split("\n")
    .find(line => line.startsWith("data:"))?.slice(5);
  if (payload === undefined) throw new Error("tools/list did not return data");
  const tools = listing.parse(JSON.parse(payload)).result.tools;
  for (const tool of tools) expect(Math.ceil(tool.description.length / 4)).toBeLessThanOrEqual(1500);
  expect(Math.ceil(agentCopy.instructions.length / 4)).toBeLessThanOrEqual(1000);
  const decide = tools.find(tool => tool.name === "decide");
  if (decide === undefined) throw new Error("Missing decide tool");
  const definitions = z.record(z.string(), z.unknown()).parse(decide.inputSchema.$defs);
  expect(Object.keys(definitions).length).toBeLessThan(Object.keys(decisionContract.$defs).length);
  const original = new Map(Object.entries(decisionContract.$defs));
  for (const [name, definition] of Object.entries(definitions)) {
    if (name !== "DecideRequest") expect(definition).toEqual(original.get(name));
  }
  // DecideRequest differs only by the MCP bounded defaults (MODEL-293).
  const request = decisionContract.$defs.DecideRequest;
  expect(definitions.DecideRequest).toEqual({
    ...request,
    properties: {
      ...request.properties,
      explain: { ...request.properties.explain, default: "none" },
      limit: { ...request.properties.limit, default: 10 },
      fields: { ...request.properties.fields, default: ["model_rank", "cost_per_task", "estimates", "p_best"] },
    },
  });
  // Record actual SDK tools/list output for pipeline.agent_overhead, when requested.
  const output = process.env.MODELSPEC_TOOL_MEASURE_OUTPUT;
  if (output) writeFileSync(output, JSON.stringify(tools, null, 2) + "\n");
});
