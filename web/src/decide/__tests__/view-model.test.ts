import { describe, expect, it } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import { decisionSchema } from "../adapter/contract";
import {
  mapDecisionToViewModel,
  toDecisionSpec,
} from "../adapter/view-model";
import { parseTask } from "../engine/reference";
import { baseSpec } from "../state/spec";

const fixture = decisionSchema.parse(fixtureJson);

describe("the hosted Decision view-model mapper", () => {
  it("projects the canvas, Pareto frontier, winning strip and shortlist from sourced values", () => {
    const spec = { ...baseSpec, bench: "quality", bar: 70 };
    const view = mapDecisionToViewModel(fixture, spec, {
      axis: "task$",
      dismissed: [],
    });

    expect(view.explanation.feasible.map((row) => row.m.id)).toEqual([
      "delta",
      "beta",
      "gamma",
      "alpha",
    ]);
    expect(view.frontier.map((row) => row.m.id)).toEqual([
      "delta",
      "beta",
      "gamma",
      "alpha",
    ]);
    expect(view.winning_strip.length).toBeGreaterThan(1);
    expect(view.explanation.shortlist.top?.m.id).toBe("delta");
    expect(view.explanation.shortlist.clears?.m.id).toBe("beta");
    expect(view.explanation.shortlist.open?.m.id).toBe("beta");
    expect(view.explanation.shortlist.value?.m.id).toBeDefined();
  });

  it("does not plot a value when the decision returned no source for it", () => {
    const withoutPriceOrigins = {
      ...fixture,
      number_origins: fixture.number_origins.filter(
        (origin) =>
          !origin.records.some((record) =>
            record.includes("offering.price.input"),
          ),
      ),
    };
    const view = mapDecisionToViewModel(
      withoutPriceOrigins,
      { ...baseSpec, bench: "quality" },
      {
      axis: "in$",
      dismissed: [],
      },
    );

    expect(view.explanation.inScope.every((row) => row.best.o.in === null)).toBe(true);
    expect(view.not_plotted.in$).toEqual([
      "lab/delta",
      "lab/beta",
      "lab/gamma",
      "lab/alpha",
    ]);
  });

  it("keeps null uncertainty explicit", () => {
    const view = mapDecisionToViewModel(fixture, { ...baseSpec, bench: "quality" }, {
      axis: "task$",
      dismissed: [],
    });
    expect(view.explanation.feasible.every((row) => row.capR?.ci === null)).toBe(true);
    expect(view.results.every((result) => result.p_best === null)).toBe(true);
  });
});

it("turns the deterministic task parse into conditions and never sends free text", () => {
  const parsed = parseTask("Refactor a large Rust codebase, precision matters");
  const spec = toDecisionSpec(
    {
      ...baseSpec,
      task: "Refactor a large Rust codebase, precision matters",
      bench: parsed.bench,
      w: parsed.w,
      conds: parsed.conds,
    },
    "full",
  );

  expect(spec).not.toHaveProperty("task");
  expect(spec.task_type).toBe("refactor");
  expect(spec.where).toContain("model.class = text-generator");
  expect(spec.where).toContain("model.context_window >= 200000");
  expect(spec.where).toContain("codebench_pro >= 50 @independent");
  expect(spec.explain).toBe("full");
});
