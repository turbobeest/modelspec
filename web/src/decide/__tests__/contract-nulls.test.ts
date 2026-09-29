import { expect, it } from "vitest";
import fullJson from "../__fixtures__/compact-full.json";
import codingJson from "../__fixtures__/plans-coding-full.json";
import { decisionSchema } from "../adapter/contract";

// The engine serialises absent optional fields as null (2026-09-29: the live
// page showed "invalid_response" for every spec until the schema accepted it).
it("accepts the engine's nulls for optional fields and its with_estate block", () => {
  const decision = structuredClone(fullJson) as Record<string, unknown> & {
    results: Record<string, unknown>[];
  };
  decision.benchmark_exclusions = null;
  decision.with_estate = null;
  for (const result of decision.results) {
    result.refinement_estimates = null;
    for (const c of result.contributions as Record<string, unknown>[]) c.refinement = null;
  }
  const parsed = decisionSchema.safeParse(decision);
  expect(parsed.success, JSON.stringify(parsed.error?.issues.slice(0, 3))).toBe(true);

  // MODEL-202 parses with_estate strictly: the engine's own block passes, a
  // block without its gap or with a field the page does not know does not.
  decision.with_estate = structuredClone(codingJson.with_estate);
  expect(decisionSchema.safeParse(decision).success).toBe(true);
  decision.with_estate = { status: "no_feasible", results: [] };
  expect(decisionSchema.safeParse(decision).success).toBe(false);
  decision.with_estate = { ...structuredClone(codingJson.with_estate), leaked: true };
  expect(decisionSchema.safeParse(decision).success).toBe(false);
});
