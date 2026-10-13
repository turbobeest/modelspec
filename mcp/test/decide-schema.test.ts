import { expect, it } from "vitest";
import { compactDecideSchema } from "../src/server";
import { z } from "zod";
import decisionContract from "../../docs/decision-contract.schema.json";

it("keeps a property named title and drops null defaults", () => {
  expect(compactDecideSchema({
    type: "object",
    title: "Wrapper",
    properties: {
      title: { type: "string", title: "Title", default: null },
      count: { type: "integer", default: 1, title: "Count" },
    },
    patternProperties: {
      "^title$": { title: "Pattern", type: "string" },
    },
  })).toEqual({
    type: "object",
    properties: {
      title: { type: "string" },
      count: { type: "integer", default: 1 },
    },
    patternProperties: {
      "^title$": { type: "string" },
    },
  });
});

it("refuses a changed condition union", () => {
  expect(() => compactDecideSchema({
    $defs: {
      DecideRequest: {
        properties: {
          where: { items: { anyOf: [{ type: "string" }, { $ref: "#/$defs/Compare" }] } },
        },
      },
    },
  })).toThrow(/condition union changed/);
});

it("decodes hardware estimates separately from facts using the published contract", () => {
  const estimate = z.fromJSONSchema({
    ...decisionContract.$defs.HardwareEstimate, $defs: decisionContract.$defs,
  });
  const known = {
    device: "nvidia_dgx_spark", facet: "hardware.decode_tps_estimate", value: 25.1,
    unit: "tokens_per_second", quantisation: "bf16", interval: { low: 12.6, high: 30.5 },
    formula: "Estimate at bf16", records: ["lab/gemma#model.parameters_active"],
    source_ids: ["src-lab-docs"],
  };
  expect(estimate.parse(known)).toMatchObject(known);
  const missing = {
    ...known, value: null, interval: undefined,
    unknown_reason: "verified positive parameters_active is missing; no fallback to parameters_total",
  };
  expect(estimate.parse(missing)).toMatchObject({
    value: null, quantisation: "bf16", interval: null,
    unknown_reason: "verified positive parameters_active is missing; no fallback to parameters_total",
  });
  expect(estimate.safeParse({ ...known, interval: { low: -1, high: 30.5 } }).success).toBe(false);
  const fact = z.fromJSONSchema(decisionContract.$defs.ShownFact);
  expect(fact.safeParse({ facet: "model.parameters_total", value: 25_800_000_000,
                         record_id: "lab/gemma#model.parameters_total", device: "nvidia_dgx_spark" }).success).toBe(false);
});
