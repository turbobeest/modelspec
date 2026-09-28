import { McpServer } from "@modelcontextprotocol/server";
import { createMcpHandler } from "agents/mcp/server";
import { z } from "zod";

import decisionContract from "../../docs/decision-contract.schema.json";
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
  "decide",
  "vocab",
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

type JsonSchemaObject = Exclude<
  Parameters<typeof z.fromJSONSchema>[0],
  boolean
>;

function decisionSpecJsonSchema(): JsonSchemaObject {
  if (
    decisionContract.$schema !== "https://json-schema.org/draft/2020-12/schema" ||
    !("Spec" in decisionContract.$defs)
  ) {
    throw new Error("decision-contract.schema.json has no decision Spec definition");
  }
  return {
    $schema: decisionContract.$schema,
    $defs: decisionContract.$defs,
    $ref: "#/$defs/Spec",
  } as JsonSchemaObject;
}

const decisionSpecSchema = decisionSpecJsonSchema();
const decisionSpecValidator = z.fromJSONSchema(decisionSpecSchema);
const decisionSpecInput = {
  "~standard": {
    version: 1 as const,
    vendor: "modelspec",
    validate(value: unknown) {
      const result = decisionSpecValidator.safeParse(value);
      return result.success ? { value } : { issues: result.error.issues };
    },
    jsonSchema: {
      input: () => decisionSpecSchema,
      output: () => decisionSpecSchema,
    },
  },
};

const vocabInput = z.object({
  section: z
    .enum([
      "facets",
      "benchmarks",
      "domains",
      "providers",
      "task_types",
      "coverage",
    ])
    .optional()
    .describe("Return only this vocabulary section"),
});

const SPEC_GUIDANCE =
  "Read vocab first for valid facet ids. Put Musts in where: these gates exclude. " +
  "Put Prefers in optimize.weights: weights rank and never exclude. Unknown values " +
  "go to may_qualify instead of being dropped. Pin snapshot for reproducibility. " +
  "Example for a coding agent on a budget: " +
  '{"spec_version":1,"snapshot":"latest","capabilities":{"software_engineering":"required"},' +
  '"where":["model.class = text-generator","model.context_window >= 200000",' +
  '"offering.cost_per_task <= 0.25"],"optimize":{"weights":' +
  '{"software_engineering":0.6,"-offering.cost_per_task":0.4}}}. ';

type DecisionBody = {
  status?: unknown;
  results?: unknown;
  may_qualify?: unknown;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function decisionSummary(body: unknown): string {
  const decision: DecisionBody = isRecord(body) ? body : {};
  const status = typeof decision.status === "string" ? decision.status : "unknown";
  const results = Array.isArray(decision.results) ? decision.results : [];
  const models = results
    .flatMap((result) => {
      if (!isRecord(result) || !isRecord(result.offering)) return [];
      const model = result.offering.model;
      return typeof model === "string" ? [model] : [];
    })
    .filter((model, index, all) => all.indexOf(model) === index)
    .slice(0, 5);
  const mayQualify = Array.isArray(decision.may_qualify)
    ? decision.may_qualify.length
    : 0;
  return (
    `status: ${status}; top models: ${models.length ? models.join(", ") : "none"}; ` +
    `may qualify: ${mayQualify}`
  );
}

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

  server.registerTool(
    "decide",
    {
      description:
        "Downselect models by proxying POST https://api.modelspec.dev/v1/decide. " +
        SPEC_GUIDANCE +
        "The decision response is returned unchanged with a short summary. " +
        "Authorization from the MCP client is forwarded. " +
        NULL_RULE,
      inputSchema: decisionSpecInput,
    },
    async (spec) => {
      const origin = `${env.RANK_API_ORIGIN.replace(/\/$/, "")}/v1/decide`;
      const envelope = await fetchOrigin(
        origin,
        postInit(spec, authorization),
        env.RANK,
      );
      const result = asToolResult(envelope);
      if (result.isError) return result;
      return {
        ...result,
        content: [
          ...result.content,
          { type: "text" as const, text: decisionSummary(envelope.body) },
        ],
      };
    },
  );

  server.registerTool(
    "vocab",
    {
      description:
        "Read the decision vocabulary from the public static site before writing a " +
        "decide spec. It lists valid facet ids, benchmarks, domains, providers, task " +
        "types, and coverage. Pass section to return only one section. " +
        SPEC_GUIDANCE,
      inputSchema: vocabInput,
    },
    async ({ section }) => {
      const origin = `${env.EXPORT_ORIGIN.replace(/\/$/, "")}/api/decision/vocabulary.json`;
      const envelope = await fetchOrigin(origin);
      if (envelope.status < 400 && section && isRecord(envelope.body)) {
        envelope.body = envelope.body[section];
      }
      return asToolResult(envelope);
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
