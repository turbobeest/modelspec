/// <reference types="node" />
import { readFileSync } from "node:fs";
import Ajv from "ajv/dist/2020";
import addFormats from "ajv-formats";
import { expect, it } from "vitest";
import { fictionalEngine, templates } from "../adapter";
import { baseSpec } from "../state/spec";
const ajv = new Ajv({ strict: false, allErrors: true });
addFormats(ajv);
const schema = JSON.parse(
  readFileSync("../docs/decision-contract.schema.json", "utf8"),
);
const validate = ajv.compile({
  ...schema,
  anyOf: undefined,
  $ref: "#/$defs/Decision",
});
it.each([
  ...templates.map((t) => t.spec),
  baseSpec,
  { ...baseSpec, conds: [...baseSpec.conds, { f: "task$" as const, max: 0 }] },
])("maps the sample into the actual Python contract JSON schema", (spec) => {
  const {
    explanation,
    near_misses,
    questions,
    frontier,
    winning_strip,
    ...contract
  } = fictionalEngine.decide(spec);
  void explanation;
  void near_misses;
  void questions;
  void frontier;
  void winning_strip;
  expect(validate(contract), JSON.stringify(validate.errors, null, 2)).toBe(
    true,
  );
});
