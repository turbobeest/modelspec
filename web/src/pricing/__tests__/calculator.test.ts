import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

// The production asset is deliberately the calculator's single implementation.
// @ts-expect-error JavaScript production asset has no declaration file.
import { calculate, packCost } from "../../../../pipeline/pricing_assets/pricing.js";

const repoRoot = resolve(process.cwd(), "..");
const python = process.env.PYTHON ?? "python3";
const generated = execFileSync(python, [
  "-c",
  "import json; from pipeline.pricing import calculator_data, load_tiers; print(json.dumps(calculator_data(load_tiers('.'))))",
], { cwd: repoRoot, encoding: "utf8", env: { ...process.env, PYTHONPATH: repoRoot } });
const data = JSON.parse(generated);

function brutePackCost(credits: number, packs: { credits: number; usd: number }[]): number {
  let best = Infinity;
  const visit = (index: number, covered: number, usd: number): void => {
    if (usd >= best) return;
    if (covered >= credits) {
      best = usd;
      return;
    }
    if (index === packs.length) return;
    const pack = packs[index];
    const maxCount = Math.ceil((credits - covered) / pack.credits);
    for (let count = 0; count <= maxCount; count += 1) {
      visit(index + 1, covered + count * pack.credits, usd + count * pack.usd);
    }
  };
  visit(0, 0, 0);
  return best;
}

describe("pricing calculator", () => {
  it.each([[21_000, 55], [30_000, 85]])(
    "finds the exact packs-only cover for %i credits", (credits, usd) => {
      expect(packCost(credits, data.packs).usd).toBe(usd);
      expect(packCost(credits, [...data.packs].reverse()).usd).toBe(usd);
    },
  );

  it("matches brute force for deterministic random pack sets and credit targets", () => {
    let seed = 0x339;
    const random = (): number => {
      seed = (seed * 1_664_525 + 1_013_904_223) >>> 0;
      return seed / 0x1_0000_0000;
    };
    for (let set = 0; set < 20; set += 1) {
      const packs = Array.from({ length: 3 }, () => ({
        credits: 1 + Math.floor(random() * 10),
        usd: 1 + Math.floor(random() * 12),
      }));
      for (let credits = 1; credits <= 40; credits += 1) {
        expect(packCost(credits, packs).usd).toBe(brutePackCost(credits, packs));
      }
    }
  });

  it("prefers a non-subscription option on an exact tie", () => {
    const tied = calculate(data, { decisions: 100, full: false, checks: 100 });
    expect(tied.options.filter(({ usd }: { usd: number }) => usd === 50)
      .map(({ name }: { name: string }) => name)).toEqual(["Packs only", "Team plan"]);
    expect(tied.best.name).toBe("Packs only");
  });

  it("omits pay per call when the production switches are not live", () => {
    const result = calculate({ ...data, payPerCall: false }, {
      decisions: 1_000, full: false, checks: 0,
    });
    expect(result.options.map(({ name }: { name: string }) => name))
      .not.toContain("Pay per call (x402)");
  });

  it.each([
    [100, false, 0, "Solo plan", 10], [100, false, 100, "Packs only", 50],
    [100, false, 1_000, "Solo plan", 310], [100, true, 0, "Solo plan", 20],
    [100, true, 100, "Team plan", 50], [100, true, 1_000, "Solo plan", 320],
    [1_000, false, 0, "Team plan", 50], [1_000, false, 100, "Packs only", 100],
    [1_000, false, 1_000, "Team plan", 350], [1_000, true, 0, "Packs only", 135],
    [1_000, true, 100, "Team plan", 150], [1_000, true, 1_000, "Packs only", 435],
    [10_000, false, 0, "Packs only", 600], [10_000, false, 100, "Packs only", 650],
    [10_000, false, 1_000, "Packs only", 900], [10_000, true, 0, "Packs only", 1_200],
    [10_000, true, 100, "Packs only", 1_250], [10_000, true, 1_000, "Packs only", 1_500],
    [100_000, false, 0, "Packs only", 6_000], [100_000, false, 100, "Packs only", 6_050],
    [100_000, false, 1_000, "Packs only", 6_300], [100_000, true, 0, "Packs only", 12_000],
    [100_000, true, 100, "Packs only", 12_050], [100_000, true, 1_000, "Packs only", 12_300],
  ])("chooses the exact cheapest option for %i decisions, full=%s, checks=%i", (
    decisions, full, checks, name, usd,
  ) => {
    expect(calculate(data, { decisions, full, checks }).best).toMatchObject({ name, usd });
  });
});
