import { writeFileSync } from "node:fs";
import { expect, it } from "vitest";
import { z } from "zod";
import { mcpHandler } from "../src/server";
import agentCopy from "../src/agent-copy.json";
import decisionContract from "../../docs/decision-contract.schema.json";
import mcpTools from "../../qa/fixtures/mcp-tools.json";

const CONDITION_UNION = [
  { type: "string" },
  { $ref: "#/$defs/Compare" },
  { $ref: "#/$defs/Window" },
  { $ref: "#/$defs/InSet" },
  { $ref: "#/$defs/Known" },
  { $ref: "#/$defs/AnyOf" },
  { $ref: "#/$defs/AllOf" },
  { $ref: "#/$defs/NotOf" },
];

function reachableDefinitionNames(): string[] {
  const selected = new Set<string>();
  const pending = ["DecideRequest"];
  while (pending.length) {
    const name = pending.pop();
    if (name === undefined || selected.has(name)) continue;
    const definition = decisionContract.$defs[name as keyof typeof decisionContract.$defs];
    if (definition === undefined) throw new Error(`Missing decision definition ${name}`);
    selected.add(name);
    for (const match of JSON.stringify(definition).matchAll(/#\/\$defs\/([^" ]+)/g)) {
      pending.push(match[1]);
    }
  }
  return [...selected];
}

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
  const recorded = mcpTools.tools.find(tool => tool.name === "decide");
  if (recorded === undefined) throw new Error("mcp-tools.json is missing decide");
  // tools/list is the schema MCP clients receive; the fixture is what the harness counts.
  // The SDK adds a root type of object beside $ref. Every other keyword matches.
  const listed = { ...decide.inputSchema };
  expect(listed.type).toBe("object");
  delete listed.type;
  expect(listed).toEqual(recorded.input_schema);
  const definitions = z.record(z.string(), z.unknown()).parse(decide.inputSchema.$defs);
  expect(Object.keys(definitions).sort()).toEqual([...reachableDefinitionNames(), "Condition"].sort());
  expect(definitions.Condition).toEqual({ anyOf: CONDITION_UNION });
  // Record actual SDK tools/list output for pipeline.agent_overhead, when requested.
  const output = process.env.MODELSPEC_TOOL_MEASURE_OUTPUT;
  if (output) writeFileSync(output, JSON.stringify(tools, null, 2) + "\n");
});
