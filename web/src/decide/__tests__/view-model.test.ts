import { describe, expect, it } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import { decisionSchema } from "../adapter/contract";
import {
  mapDecisionToViewModel,
  toDecisionSpec,
} from "../adapter/view-model";
import { reason } from "../adapter";
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

  it("presents candidate-grained decisions as models with offering variants", () => {
    const view = mapDecisionToViewModel(
      fixture,
      { ...baseSpec, bench: "quality" },
      { axis: "task$", dismissed: [] },
    );

    expect(view.population).toEqual({ models: 4, offerings: 8 });
    expect(view.explanation.funnel.map(({ label, n }) => [label, n])).toEqual([
      ["All models", 4],
      ["Type: text generator", 4],
      ["Has a provider", 4],
    ]);
    expect(view.explanation.rows.map((row) => row.m.id)).toEqual([
      "delta",
      "beta",
      "gamma",
      "alpha",
    ]);
    expect(view.explanation.rows.every((row) => row.m.offerings.length === 1)).toBe(true);
    expect(view.explanation.excluded).toEqual([]);
  });

  it("drops candidate-level near misses unless a model's best offering misses one condition", () => {
    const view = mapDecisionToViewModel(
      fixture,
      { ...baseSpec, bench: "quality" },
      { axis: "task$", dismissed: [] },
    );

    expect(fixture.near_misses).toHaveLength(4);
    expect(view.nearMisses).toEqual([]);
  });

  it("reads model-grained funnel, eliminations and near misses from contract 1.6", () => {
    const firstOffering = fixture.results[0].offering;
    const hosted = decisionSchema.parse({
      ...fixture,
      contract_version: "1.6",
      results: fixture.results.filter((result) => result.offering.model !== firstOffering.model),
      near_misses: [
        {
          values: [],
          offering: firstOffering,
          condition: "offering.provider = cloud",
          facet: "offering.provider",
          value: "cloud",
          distance: null,
          unit: null,
          records: [],
        },
      ],
      eliminated: {
        ...fixture.eliminated,
        funnel: fixture.eliminated.funnel.map((step) => ({
          ...step,
          models_before: 4,
          models_after: 4,
          offerings_before: 4,
          offerings_after: 4,
        })),
        model_groups: [
          {
            model: firstOffering.model,
            model_elimination: null,
            offerings: [
              {
                values: [],
                offering: firstOffering,
                unit: null,
                records: [],
                condition: "offering.provider = cloud",
                value: "cloud",
              },
            ],
          },
        ],
      },
    });
    const view = mapDecisionToViewModel(
      hosted,
      {
        ...baseSpec,
        bench: "quality",
        conds: [{ f: "facet", facet: "offering.provider", op: "=", value: "cloud" }],
      },
      { axis: "task$", dismissed: [] },
    );

    expect(view.population).toEqual({ models: 4, offerings: 4 });
    expect(view.explanation.funnel.map(({ n }) => n)).toEqual([4, 4, 4]);
    expect(view.nearMisses).toHaveLength(1);
    expect(view.nearMisses[0].off.o.id).toBe(
      [firstOffering.provider, firstOffering.model, firstOffering.region, firstOffering.tier]
        .filter((part) => part !== null)
        .join("/"),
    );
  });
});

describe("model names", () => {
  const spec = { ...baseSpec, bench: "quality" };

  it("uses each card's display name and lab name from the vocabulary", () => {
    const view = mapDecisionToViewModel(fixture, spec, {
      axis: "task$",
      dismissed: [],
      models: {
        "lab/delta": { display_name: "Delta 4.7", lab: "lab", lab_name: "Lab Inc." },
        "lab/beta": { display_name: "GLM-5.2", lab: "lab", lab_name: null },
      },
    });
    const byId = new Map(view.explanation.rows.map((row) => [row.m.id, row.m]));
    expect(byId.get("delta")).toMatchObject({ name: "Delta 4.7", labName: "Lab Inc." });
    expect(byId.get("beta")).toMatchObject({ name: "GLM-5.2", labName: "lab" });
  });

  it("shows the model ID verbatim when a name is missing, never a title-cased slug", () => {
    const view = mapDecisionToViewModel(fixture, spec, { axis: "task$", dismissed: [] });
    const names = view.explanation.rows.map((row) => row.m.name);
    expect(names).toContain("lab/gamma");
    expect(names.some((name) => /^[A-Z]/.test(name))).toBe(false);
  });
});

it("says what a may-qualify row does not know once, without a doubled prefix", () => {
  const withMay = {
    ...fixture,
    results: fixture.results.filter((result) => result.offering.model !== "lab/alpha"),
    may_qualify: [
      {
        model: "lab/alpha",
        offering: fixture.results.find((result) => result.offering.model === "lab/alpha")!
          .offering,
        unknown: ["quality"],
      },
    ],
  };
  const view = mapDecisionToViewModel(
    decisionSchema.parse(withMay),
    { ...baseSpec, bench: "quality", conds: [{ f: "bench", b: "quality", min: 70 }] },
    { axis: "task$", dismissed: [] },
  );
  const row = view.explanation.may.find((candidate) => candidate.m.id === "alpha")!;
  expect(reason(row)).not.toMatch(/unknown/i);
  expect(reason(row)).toBe("Quality not known");
  expect(row.best.t.map((test) => test.why ?? "").join(" ")).not.toMatch(/unknown: /i);
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
