// Contract 1.4 (MODEL-163): a `full` decision lists each source once, names it
// by ID from the origins and from each shown fact. The fixtures are the
// engine's own answers (tests/test_decide_page_fixtures.py).
import { afterEach, describe, expect, it, vi } from "vitest";
import fullJson from "../__fixtures__/compact-full.json";
import summaryJson from "../__fixtures__/compact-summary.json";
import { decisionSchema } from "../adapter";
import { mapDecisionToViewModel } from "../adapter/view-model";
import { baseSpec } from "../state/spec";

const full = decisionSchema.parse(fullJson);
const summary = decisionSchema.parse(summaryJson);
const spec = { ...baseSpec, bench: "quality", tokIn: 40_000, tokOut: 4_000 };
const view = (decision = full) =>
  mapDecisionToViewModel(decision, spec, { axis: "task$", dismissed: [] });

afterEach(() => vi.unstubAllGlobals());

describe("the compact full decision", () => {
  it("parses, with sources listed once and origins naming them by ID", () => {
    expect(full.contract_version).toBe("2.8");
    expect(full.answer?.kind).toBe("separated");
    expect(full.sources.map((source) => source.id)).toEqual([
      "src-board",
      "src-lab-docs",
      "src-pricing",
    ]);
    expect(full.number_origins.every((origin) => origin.sources.length === 0)).toBe(true);
    expect(full.number_origins.some((origin) => origin.source_ids.length > 0)).toBe(true);
  });

  it("shows a candidate's facts through their source IDs", () => {
    const alpha = view().explanation.feasible[0];
    expect(alpha.m.id).toBe("alpha");
    expect(alpha.best.o.in).toBe(3);
    expect(alpha.best.o.out).toBe(12);
    expect(alpha.m.ctx).toBe(200_000);
    expect(alpha.m.open).toBe(false);
    expect(alpha.m.status).toBe("active");
    expect(alpha.best.o.ttft).toBe(420);
    expect(alpha.tps).toBe(95);
    expect(alpha.cap).toBe(92);
    expect(alpha.cost).toBeCloseTo(0.168);
  });

  it("does not show a fact whose source is missing from the sources table", () => {
    const unsourced = {
      ...full,
      sources: full.sources.filter((source) => source.id !== "src-pricing"),
    };
    const alpha = view(unsourced).explanation.feasible[0];
    expect(alpha.best.o.in).toBeNull();
    expect(alpha.m.ctx).toBe(200_000);
  });
});

describe("the engine's model view (MODEL-180)", () => {
  const ids = (rows: { m: { lab: string; id: string } }[]) =>
    rows.map((row) => `${row.m.lab}/${row.m.id}`);

  it("carries the flat fields and one by_model row per model", () => {
    expect(full.by_model.length).toBeGreaterThan(0);
    expect(full.results.every((result) => result.model === result.offering.model)).toBe(true);
    expect(full.results.every((result) => typeof result.cost_per_task === "number")).toBe(true);
  });

  it("groups the page's rows exactly as the engine's view does", () => {
    const mapped = view().explanation;
    const engine = (status: string) =>
      full.by_model.filter((row) => row.status === status).map((row) => row.model);
    expect(ids(mapped.feasible)).toEqual(engine("ranked"));
    expect(ids(mapped.may)).toEqual(engine("may_qualify"));
    expect(ids(mapped.excluded)).toEqual(engine("eliminated"));
  });

  it("puts every offering of a model under its row", () => {
    const mapped = view().explanation.feasible;
    full.by_model
      .filter((row) => row.status === "ranked")
      .forEach((row, index) => {
        expect(mapped[index].offs).toHaveLength(row.offerings.length);
      });
  });

  it("still groups a decision that predates by_model", () => {
    const legacy = { ...full, by_model: [] };
    const mapped = view(legacy).explanation;
    const engine = view().explanation;
    expect(ids(mapped.feasible)).toEqual(ids(engine.feasible));
    expect(ids(mapped.may)).toEqual(ids(engine.may));
    expect(ids(mapped.excluded).sort()).toEqual(ids(engine.excluded).sort());
  });
});

describe("a summary decision, when the full explanation was unavailable", () => {
  it("ranks from results, with capability from their evidence and $ per task from the formula", () => {
    const mapped = view(summary);
    expect(summary.explain).toBe("summary");
    expect(summary.top).toEqual([]);
    expect(mapped.explanation.feasible.map((row) => row.m.id)).toEqual([
      "alpha",
      "gamma",
      "beta",
    ]);
    const alpha = mapped.explanation.feasible[0];
    expect(alpha.cap).toBe(92);
    expect(alpha.capR?.src).toBe("https://board.example.org/results");
    expect(alpha.cost).toBeCloseTo(0.168);
    expect(alpha.best.o.costFormula).toContain("= 0.168 USD per task");
    // A summary shows no facts: nothing is invented for them.
    expect(alpha.best.o.in).toBeNull();
    expect(alpha.m.ctx).toBeNull();
  });
});
