import { expect, it } from "vitest";
import { compactDecideSchema } from "../src/server";

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
