import { expect, it } from "vitest";
import { decisionSchema } from "../adapter";
import { mapDecisionToViewModel, toDecisionSpec } from "../adapter/view-model";
import { baseSpec } from "../state/spec";
import type { Cond } from "../engine/types";
import { facetOptions, realBaseSpec, vocabularySchema } from "../vocabulary";
import decisionFixture from "../__fixtures__/compact-tied-full.json";
import { smallVocabulary } from "./vocab-fixtures";

it("offers architecture and active parameters from the published vocabulary", () => {
  const vocabulary = vocabularySchema.parse({
    ...smallVocabulary,
    facets: [
      {
        id: "model.architecture", label: "Architecture", definition: "Architecture family",
        subject: "model", value_type: "enum", unit: null,
        operators: ["=", "!=", "in", "not_in"], objective: false,
        preference: { kind: "value", term: { prefer: "enum value", weight: "positive number" } },
        risk: "capability", computed_by: null, known: 2, of: 2,
        values: [{ value: "MoE", count: 1 }, { value: "dense-transformer", count: 1 }],
      },
      {
        id: "model.parameters_active", label: "Active parameters", definition: "Parameters per token",
        subject: "model", value_type: "number", unit: "parameters",
        operators: ["<=", ">="], objective: true, better: "neither",
        preference: { kind: "continuous", directions: ["max", "min"], threshold: "where" },
        risk: "capability", computed_by: null, known: 2, of: 2,
        range: { min: 3_800_000_000, max: 31_000_000_000 },
      },
    ],
  });
  const options = facetOptions(vocabulary);
  expect(options.map((option) => option.label)).toEqual(expect.arrayContaining([
    "Architecture", "Active parameters",
  ]));
  const base = realBaseSpec(vocabulary);
  const conditions: Cond[] = [
    { f: "facet", facet: "model.architecture", op: "=", value: "MoE" },
    { f: "facet", facet: "model.parameters_active", op: "<=", value: 4_000_000_000 },
  ];
  const must = toDecisionSpec({ ...base, conds: conditions }, "full");
  expect(must.where).toEqual([
    "model.architecture = MoE", "model.parameters_active <= 4000000000",
  ]);
  const prefer = toDecisionSpec({
    ...base, conds: conditions.map((condition) => ({ ...condition, soft: true })),
  }, "full");
  expect(prefer.where).toEqual([
    "model.architecture = MoE soft(0.2)",
    "model.parameters_active <= 4000000000 soft(0.2)",
  ]);
});

it("retains per-device hardware estimate bounds in contract 2.16", () => {
  const payload = {
    ...decisionFixture, contract_version: "2.16",
    top: [{
      offering: { model: "lab/gemma", provider: null, region: null, tier: null }, contributions: [], evidence: [],
      facts: [],
      unknown_facets: ["model.parameters_active"],
      hardware_estimates: [{
        facet: "hardware.decode_tps_estimate", value: 25.1, unit: "tokens_per_second",
        records: ["lab/gemma#model.parameters_active", "hardware:nvidia_dgx_spark#memory"],
        source_ids: ["src-lab-docs", "spark-spec"], formula: "Estimate at bf16",
        device: "nvidia_dgx_spark", quantisation: "bf16", interval: { low: 12.6, high: 30.5 },
      }],
    }],
  };
  const decision = decisionSchema.parse(payload);
  expect(decision.top[0].facts).toEqual([]);
  expect(decision.top[0].unknown_facets).toEqual(["model.parameters_active"]);
  expect(decision.top[0].hardware_estimates?.[0].device).toBe("nvidia_dgx_spark");
  expect(decision.top[0].hardware_estimates?.[0].quantisation).toBe("bf16");
  expect(decision.top[0].hardware_estimates?.[0].interval).toEqual({ low: 12.6, high: 30.5 });
  const view = mapDecisionToViewModel(decision, { ...baseSpec, bench: "quality" }, { axis: "ctx", dismissed: [] });
  expect(view.top[0].unknown_facets).toEqual(["model.parameters_active"]);
  expect(view.top[0].hardware_estimates?.[0].interval).toEqual({ low: 12.6, high: 30.5 });
  const invalid = {
    ...payload, top: [{ ...payload.top[0], hardware_estimates: [
      { ...payload.top[0].hardware_estimates[0], interval: { low: 30.5, high: 12.6 } },
    ] }],
  };
  expect(decisionSchema.safeParse(invalid).success).toBe(false);
  const unknown = decisionSchema.parse({
    ...payload, top: [{ ...payload.top[0], hardware_estimates: [{
      ...payload.top[0].hardware_estimates[0], value: null, interval: undefined,
      unknown_reason: "verified positive parameters_active is missing; no fallback to parameters_total",
    }] }],
  });
  expect(unknown.top[0].hardware_estimates?.[0].unknown_reason).toBe(
    "verified positive parameters_active is missing; no fallback to parameters_total",
  );
});
