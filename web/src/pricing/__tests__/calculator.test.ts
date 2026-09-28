import { describe, expect, it } from "vitest";

// The production asset is deliberately the calculator's single implementation.
// @ts-expect-error JavaScript production asset has no declaration file.
import { calculate } from "../../../../pipeline/pricing_assets/pricing.js";

const data = {
  plans: [
    { name: "Solo", credits: 4_000, usd: 10 },
    { name: "Team", credits: 30_000, usd: 50 },
  ],
  packs: [
    { credits: 1_250, usd: 5 },
    { credits: 7_500, usd: 25 },
    { credits: 20_000, usd: 50 },
    { credits: 50_000, usd: 100 },
  ],
  weights: { decide: 1, decideFull: 2, rank: 1, check: 5 },
  perCall: 5 / 1_250,
};

describe("pricing calculator", () => {
  it.each([
    [100, "Solo plan", 10],
    [1_000, "Team plan", 50],
    [10_000, "Packs only", 600],
  ])("finds the cheapest summary option for %i decisions a day", (decisions, name, usd) => {
    expect(calculate(data, { decisions, full: false, checks: 0 }).best).toMatchObject({ name, usd });
  });

  it("applies full-explanation and policy-check weights", () => {
    expect(calculate(data, { decisions: 100, full: true, checks: 100 }).monthly).toBe(21_000);
    expect(calculate(data, { decisions: 100, full: false, checks: 0 }).monthly).toBe(3_000);
  });
});
