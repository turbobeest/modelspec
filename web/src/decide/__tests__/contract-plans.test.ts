import { expect, it } from "vitest";
import codingJson from "../__fixtures__/plans-coding-full.json";
import ownSoftwareJson from "../__fixtures__/plans-own-software-full.json";
import { decisionSchema, decisionSpecSchema } from "../adapter/contract";

// 2.6 (MODEL-200): the engine's own answers to specs with `access` and an
// estate, including plan routes whose price and break-even are null.
it.each([
  ["coding_tool", codingJson],
  ["own_software", ownSoftwareJson],
])("accepts a %s decision with plan routes", (_, json) => {
  const parsed = decisionSchema.safeParse(json);
  expect(parsed.success, JSON.stringify(parsed.error?.issues.slice(0, 3))).toBe(true);
  expect(parsed.data?.results.some((result) => (result.plans ?? []).length > 0)).toBe(true);
});

it("keeps a null price and break-even on a plan route", () => {
  const routes = decisionSchema
    .parse(ownSoftwareJson)
    .results.flatMap((result) => result.plans ?? []);
  expect(routes.map((route) => [route.plan, route.price, route.break_even_tasks_per_month])).toEqual(
    [["anthropic/subscription/team-api", null, null]],
  );
});

it("accepts access as a bare kind or an object, and refuses an unknown kind", () => {
  const spec = { spec_version: 1, optimize: { max: "model.context_window" } };
  expect(decisionSpecSchema.safeParse({ ...spec, access: "own_software" }).success).toBe(true);
  expect(
    decisionSpecSchema.safeParse({ ...spec, access: { kind: "coding_tool", harness: "claude-code" } })
      .success,
  ).toBe(true);
  expect(decisionSpecSchema.safeParse({ ...spec, access: "browser" }).success).toBe(false);
});
