import { expect, it } from "vitest";
import codingJson from "../__fixtures__/plans-coding-full.json";
import { decisionSchema } from "../adapter/contract";

const closedPlan = "anthropic/subscription/max-20x";
const closedReason = "Claude Max 20x (anthropic/subscription/max-20x) is closed to new buyers; only existing subscribers can use it.";
const exclusions = [{ plan: closedPlan, reason: closedReason }];

it.each(["2.17", "2.18"])("accepts a complete %s decision without availability fields", (version) => {
  const decision = decisionSchema.parse({ ...codingJson, contract_version: version });

  expect(decision.contract_version).toBe(version);
  expect(decision).not.toHaveProperty("excluded_plans");
  expect(decision.with_estate).not.toHaveProperty("excluded_plans");
  expect(decision.with_estate?.results.map((result) => result.estate)).toEqual(
    codingJson.with_estate.results.map((result) => result.estate),
  );
});

it("retains the complete decision's unavailable-plan reasons and the held plan's availability", () => {
  const decision = decisionSchema.parse({
    ...codingJson,
    contract_version: "2.18",
    excluded_plans: exclusions,
    with_estate: {
      ...codingJson.with_estate,
      excluded_plans: [{ plan: "anthropic/subscription/retired", reason: "The plan is retired and cannot be used, even by existing subscribers." }],
      results: codingJson.with_estate.results.map((result) => ({
        ...result,
        estate: { ...result.estate, availability: "existing_subscribers_only" },
      })),
    },
  });

  expect(decision.excluded_plans).toEqual([{ plan: closedPlan, reason: closedReason }]);
  expect(decision.with_estate?.excluded_plans).toEqual([
    { plan: "anthropic/subscription/retired", reason: "The plan is retired and cannot be used, even by existing subscribers." },
  ]);
  expect(decision.with_estate?.results.map((result) => result.estate.availability)).toEqual([
    "existing_subscribers_only", "existing_subscribers_only",
  ]);
});

it.each(["open", "existing_subscribers_only", "retired", null])(
  "accepts the contract's %s holding availability",
  (availability) => {
    const decision = decisionSchema.parse({
      ...codingJson,
      contract_version: "2.18",
      with_estate: {
        ...codingJson.with_estate,
        results: codingJson.with_estate.results.map((result) => ({
          ...result,
          estate: { ...result.estate, availability },
        })),
      },
    });

    expect(decision.with_estate?.results.map((result) => result.estate.availability)).toEqual([
      availability, availability,
    ]);
  },
);

it.each([
  null,
  [{ plan: "", reason: closedReason }],
  [{ plan: "a".repeat(121), reason: closedReason }],
  [{ plan: closedPlan, reason: null }],
  [{ plan: closedPlan }],
  [{ plan: closedPlan, reason: closedReason, unexpected: true }],
])("refuses malformed availability exclusions without relaxing the complete decoder", (excluded_plans) => {
  expect(decisionSchema.safeParse({ ...codingJson, contract_version: "2.18", excluded_plans }).success).toBe(false);
  expect(decisionSchema.safeParse({
    ...codingJson,
    contract_version: "2.18",
    with_estate: { ...codingJson.with_estate, excluded_plans },
  }).success).toBe(false);
});

it("refuses an unknown holding availability value", () => {
  expect(decisionSchema.safeParse({
    ...codingJson,
    contract_version: "2.18",
    with_estate: {
      ...codingJson.with_estate,
      results: codingJson.with_estate.results.map((result) => ({
        ...result,
        estate: { ...result.estate, availability: "unknown" },
      })),
    },
  }).success).toBe(false);
});
