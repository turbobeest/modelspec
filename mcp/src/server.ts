import { McpServer } from "@modelcontextprotocol/server";
import { createMcpHandler } from "agents/mcp/server";
import { z } from "zod";

import {
  asToolResult,
  fetchOrigin,
  incomingAuthorization,
  modelCardUrl,
} from "./origin";

export const TOOL_NAMES = [
  "rank",
  "model_info",
  "list_use_cases",
  "policy_check",
] as const;

const NULL_RULE =
  "Null means not researched or not published, never a guess. " +
  "Every sourced value on a card carries a URL and a read date. " +
  "This tool returns the origin's JSON plus the origin URL; it does not invent fields.";

const rankInput = z
  .object({
    use_case: z
      .string()
      .describe("Ranking profile id, as published in /api/rank/profiles.json"),
    environment: z
      .object({
        hardware: z.string().nullable().optional(),
        hosting: z.enum(["local", "self_hosted", "managed_api"]).nullable().optional(),
        runtime: z.string().nullable().optional(),
      })
      .optional(),
    constraints: z
      .object({
        open_weights: z.boolean().nullable().optional(),
        max_cost_per_million_input_tokens: z.number().nullable().optional(),
        price_sensitivity: z.number().nullable().optional(),
        include_rehosts: z.boolean().nullable().optional(),
      })
      .optional(),
    limit: z.number().int().min(0).max(100).optional(),
  })
  .passthrough();

const policyInput = z
  .object({
    policy: z
      .object({
        name: z.string().optional(),
        licence: z
          .object({
            allowed: z.array(z.string()).optional(),
            prohibited: z.array(z.string()).optional(),
          })
          .optional(),
        origin: z
          .object({
            permitted_countries: z.array(z.string()).optional(),
            prohibited_countries: z.array(z.string()).optional(),
          })
          .optional(),
        residency: z
          .object({
            required_regions: z.array(z.string()).optional(),
            match: z.enum(["any", "all"]).optional(),
          })
          .optional(),
        commercial_use: z
          .object({
            required: z.boolean().optional(),
            accept_restricted: z.boolean().optional(),
          })
          .optional(),
      })
      .passthrough(),
    require_no_undetermined: z.boolean().optional(),
    models: z.array(z.string()).optional(),
    platforms: z.array(z.string()).optional(),
    verdicts: z.array(z.enum(["pass", "fail", "undetermined"])).optional(),
    limit: z.number().int().min(0).max(500).optional(),
    offset: z.number().int().min(0).optional(),
  })
  .passthrough();

export type McpFactoryContext = {
  requestInfo?: Request;
};

function jsonBody(value: unknown): string {
  return JSON.stringify(value);
}

function postInit(
  body: unknown,
  authorization: string | undefined,
): RequestInit {
  const headers = new Headers({ "content-type": "application/json" });
  if (authorization) headers.set("authorization", authorization);
  return { method: "POST", headers, body: jsonBody(body) };
}

export function createModelspecServer(env: Env, mcpCtx: McpFactoryContext = {}) {
  const authorization = incomingAuthorization(mcpCtx.requestInfo);
  const server = new McpServer({
    name: "modelspec",
    version: env.BUILD_COMMIT,
  });

  server.registerTool(
    "rank",
    {
      description:
        "Rank models for a use case by proxying POST https://api.modelspec.dev/v1/rank " +
        "with this tool's arguments as the JSON body. Does not re-implement ranking. " +
        "evidence_basis is input provenance (none, unverified-legacy, mixed, " +
        "partial-verified, verified), not a quality verdict. Free tier; no key required. " +
        NULL_RULE,
      inputSchema: rankInput,
    },
    async (args) => {
      const origin = `${env.RANK_API_ORIGIN.replace(/\/$/, "")}/v1/rank`;
      return asToolResult(await fetchOrigin(origin, postInit(args, authorization), env.RANK));
    },
  );

  server.registerTool(
    "model_info",
    {
      description:
        "Read one published model card from the static export at " +
        "https://modelspec.dev/api/models/<model_id>.json (model_id is provider/slug). " +
        "The card is catalogue data, not a ranking. " +
        NULL_RULE,
      inputSchema: z.object({
        model_id: z.string().describe("Catalogue id, e.g. openai/gpt-5-6"),
      }),
    },
    async ({ model_id }) => {
      const located = modelCardUrl(env.EXPORT_ORIGIN, model_id);
      if ("error" in located) {
        return {
          content: [{ type: "text", text: located.error }],
          isError: true,
        };
      }
      return asToolResult(await fetchOrigin(located.origin));
    },
  );

  server.registerTool(
    "list_use_cases",
    {
      description:
        "List ranking profiles and the published ranking policy from " +
        "https://modelspec.dev/api/rank/profiles.json. " +
        "Floors and neutrality are data on that document. " +
        NULL_RULE,
      inputSchema: z.object({}),
    },
    async () => {
      const origin = `${env.EXPORT_ORIGIN.replace(/\/$/, "")}/api/rank/profiles.json`;
      return asToolResult(await fetchOrigin(origin));
    },
  );

  server.registerTool(
    "policy_check",
    {
      description:
        "Check a policy document per model and per platform by proxying POST " +
        "https://api.modelspec.dev/v1/policy-check with this tool's arguments as the " +
        "JSON body. Free-tier answer only unless the MCP client sent Authorization, " +
        "which is forwarded. Verdicts are pass, fail, or undetermined — undetermined " +
        "is not a pass. " +
        NULL_RULE,
      inputSchema: policyInput,
    },
    async (args) => {
      const origin = `${env.RANK_API_ORIGIN.replace(/\/$/, "")}/v1/policy-check`;
      return asToolResult(await fetchOrigin(origin, postInit(args, authorization), env.RANK));
    },
  );

  return server;
}

export function handlerOptions() {
  return {
    route: "/mcp",
    allowedHostnames: ["api.modelspec.dev", "localhost", "127.0.0.1"],
    allowedOriginHostnames: ["localhost", "127.0.0.1"],
  };
}

export function mcpHandler(env: Env) {
  return createMcpHandler(
    (ctx) => createModelspecServer(env, ctx),
    handlerOptions(),
  );
}
